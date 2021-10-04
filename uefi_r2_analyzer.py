#!/usr/bin/env python3
#
# SPDX-License-Identifier: GPL-3.0+
#
# pylint: disable=invalid-name,missing-module-docstring,missing-function-docstring

# uefi_r2: tools for analyzing UEFI firmware using radare2/rizin

import json
import os

import click

from uefi_r2 import UefiAnalyzer, UefiRule, UefiScanner, uefi_smm


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

    uefi_analyzer = UefiAnalyzer(image_path=image_path)

    summary = uefi_analyzer.get_summary()
    uefi_analyzer.close()

    if out:
        with open(out, "w") as f:
            json.dump(summary, f, indent=4)
    else:
        print(json.dumps(summary, indent=4))

    return True


@click.command()
@click.argument("image_path")
@click.option("-r", "--rule", help="The path to the rule.")
def scan(image_path: str, rule: str) -> bool:
    """Scan input UEFI image."""

    if not os.path.isfile(image_path):
        print("{} check image path".format(click.style("ERROR", fg="red", bold=True)))
        return False
    if not (rule and os.path.isfile(rule)):
        print("{} check rule path".format(click.style("ERROR", fg="red", bold=True)))
        return False

    # on linux platforms you can pass blob via shm://
    # uefi_analyzer = UefiAnalyzer(blob=data)

    uefi_analyzer = UefiAnalyzer(image_path=image_path)

    prefix = click.style("UEFI analyzer", fg="green")
    if (
        uefi_analyzer.info["bin"]["arch"] == "x86"
        and uefi_analyzer.info["bin"]["bits"] == 32
    ):
        print(f"{prefix} ppi_list: {[x.__dict__ for x in uefi_analyzer.ppi_list]}")
        print(f"{prefix} guids: {[x.__dict__ for x in uefi_analyzer.protocol_guids]}")

    elif (
        uefi_analyzer.info["bin"]["arch"] == "x86"
        and uefi_analyzer.info["bin"]["bits"] == 64
    ):
        print(f"{prefix} nvram: {[x.__dict__ for x in uefi_analyzer.nvram_vars]}")
        print(f"{prefix} protocols: {[x.__dict__ for x in uefi_analyzer.protocols]}")
        print(f"{prefix} guids: {[x.__dict__ for x in uefi_analyzer.protocol_guids]}")

    with open(rule, "r") as f:
        rule_content = f.read()

    uefi_rule = UefiRule(rule_content=rule_content)
    prefix = click.style("UEFI rule", fg="green")
    print(f"{prefix} nvram: {[x.__dict__ for x in uefi_rule.nvram_vars]}")
    print(f"{prefix} protocols: {[x.__dict__ for x in uefi_rule.protocols]}")
    print(f"{prefix} ppi: {[x.__dict__ for x in uefi_rule.ppi_list]}")
    print(f"{prefix} guids: {[x.__dict__ for x in uefi_rule.protocol_guids]}")
    print(f"{prefix} esil: {uefi_rule.esil_rules}")
    print(f"{prefix} strings: {uefi_rule.strings}")
    print(f"{prefix} wide_strings: {uefi_rule.wide_strings}")
    print(f"{prefix} hex_strings: {uefi_rule.hex_strings}")

    scanner = UefiScanner(uefi_analyzer, uefi_rule)
    prefix = click.style("Scanner result", fg="green")
    print(f"{prefix} {uefi_rule.name} {scanner.result}")

    uefi_analyzer.close()

    return True


cli.add_command(analyze_image)
cli.add_command(scan)

if __name__ == "__main__":
    cli()
