#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-3.0+
#
# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

# fwhunt_scan: tools for analyzing UEFI firmware and checking UEFI modules with FwHunt rules

import json
import os
import pathlib
import tempfile
from typing import Dict, List

import click

from fwhunt_scan import UefiAnalyzer, UefiExtractor, UefiRule, UefiScanner


@click.group()
def cli():
    pass


@click.command()
@click.argument("image_path")
@click.option("-o", "--out", help="Output JSON file.")
def analyze_image(image_path: str, out: str) -> bool:
    """Analyze input UEFI image."""

    if not os.path.isfile(image_path):
        print("{} check image path".format(click.style("ERROR", fg="red", bold=True)))
        return False

    # on linux platforms you can pass blob via shm://
    # uefi_analyzer = UefiAnalyzer(blob=data)

    summary = None
    with UefiAnalyzer(image_path=image_path) as uefi_analyzer:
        summary = uefi_analyzer.get_summary()

    if out:
        with open(out, "w") as f:
            json.dump(summary, f, indent=4)
    else:
        print(json.dumps(summary, indent=4))

    return True


@click.command()
@click.argument("image_path")
@click.option("-r", "--rule", help="The path to the rule.", multiple=True)
def scan(image_path: str, rule: List[str]) -> bool:
    """Scan single UEFI module."""

    rules = rule

    if not os.path.isfile(image_path):
        print("{} check image path".format(click.style("ERROR", fg="red", bold=True)))
        return False
    if not all(rule and os.path.isfile(rule) for rule in rules):
        print("{} check rule(s) path".format(click.style("ERROR", fg="red", bold=True)))
        return False

    # on linux platforms you can pass blob via shm://
    # uefi_analyzer = UefiAnalyzer(blob=data)

    uefi_analyzer = UefiAnalyzer(image_path=image_path)

    uefi_rules: List[UefiRule] = list()

    for r in rules:
        with open(r, "r") as f:
            rule_content = f.read()
            uefi_rule = UefiRule(rule_content=rule_content)
            uefi_rules.append(uefi_rule)

    scanner = UefiScanner(uefi_analyzer, uefi_rules)
    prefix = click.style("Scanner result", fg="green")

    no_threat = click.style("No threat detected", fg="green")
    threat = click.style(
        "FwHunt rule has been triggered and threat detected!", fg="red"
    )

    for result in scanner.results:
        msg = threat if result.res else no_threat
        print(
            f"{prefix} {result.rule.name} (variant: {result.variant_label}) {msg} ({image_path})"
        )

    uefi_analyzer.close()

    return True


@click.command()
@click.argument("image_path")
@click.option("-r", "--rule", help="The path to the rule.", multiple=True)
@click.option("-d", "--rules_dir", help="The path to the rules directory.")
def scan_firmware(image_path: str, rule: List[str], rules_dir: str) -> bool:
    """Scan UEFI firmware image."""

    rules = list(rule)
    error_prefix = click.style("ERROR", fg="red", bold=True)
    if not rules_dir:
        if not all(rules and os.path.isfile(rule) for rule in rules):
            print(f"{error_prefix} check rule(s) path")
            return False
    else:
        rules += list(map(str, pathlib.Path(rules_dir).rglob("*.yml")))

    if not os.path.isfile(image_path):
        print(f"{error_prefix} check image path")
        return False

    # on linux platforms you can pass blob via shm://
    # uefi_analyzer = UefiAnalyzer(blob=data)

    uefi_rules: List[UefiRule] = list()

    for r in rules:
        with open(r, "r") as f:
            rule_content = f.read()
            uefi_rule = UefiRule(rule_content=rule_content)
            uefi_rules.append(uefi_rule)

    # Group rules by guids
    rules_guids: Dict[str, List[UefiRule]] = dict()
    for rule in uefi_rules:
        if rule.volume_guids is None:
            print(f"[I] Specify volume_guids in {rule.name} or use scan command")
            continue
        for guid in rule.volume_guids:
            if not guid in rules_guids:
                rules_guids[guid] = [rule]
            else:
                rules_guids[guid].append(rule)

    if not rules_guids.keys():
        print(
            f"{error_prefix} None of the rules specify volume_guids (use scan command)"
        )
        return False

    with open(image_path, "rb") as f:
        firmware_data = f.read()

    prefix = click.style("Scanner result", fg="green")
    no_threat = click.style("No threat detected", fg="green")
    threat = click.style(
        "FwHunt rule has been triggered and threat detected!", fg="red"
    )

    for volume_guid in rules_guids:
        extractor = UefiExtractor(firmware_data, volume_guid)
        if extractor.binary is None:
            for rule in rules_guids[volume_guid]:
                print(
                    f"[I] Skipping the rule {rule.name} (module not present in firmware image)"
                )
            continue

        if not extractor.binary.content:
            continue

        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f"{extractor.binary.name}_",
            suffix=f".{extractor.binary.ext}",
            dir=None,
            delete=True,
        ) as f:
            f.write(extractor.binary.content)
            uefi_analyzer = UefiAnalyzer(image_path=f.name)
            scanner = UefiScanner(uefi_analyzer, rules_guids[volume_guid])

            for result in scanner.results:
                msg = threat if result.res else no_threat
                print(
                    f"{prefix} {result.rule.name} (variant: {result.variant_label}) {msg} ({extractor.binary.name})"
                )

        uefi_analyzer.close()

    return True


cli.add_command(analyze_image)
cli.add_command(scan)
cli.add_command(scan_firmware)

if __name__ == "__main__":
    cli()
