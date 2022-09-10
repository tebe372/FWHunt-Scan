[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![fwhunt-scan CI](https://github.com/binarly-io/fwhunt-scan/actions/workflows/ci.yml/badge.svg)](https://github.com/binarly-io/fwhunt-scan/actions)
[![fwhunt-scan pypi](https://img.shields.io/pypi/v/fwhunt-scan.svg)](https://pypi.org/project/fwhunt-scan)

<p align="center">
  <img alt="fwhunt Logo" src="https://raw.githubusercontent.com/binarly-io/fwhunt-scan/master/pics/fwhunt_logo.png" width="20%">
</p>

# FwHunt Community Scanner

Tools for analyzing UEFI firmware and checking UEFI modules with [FwHunt rules](https://github.com/binarly-io/fwhunt).

# Dependencies

rizin (v0.4.1)

# Installation

Install with `pip` (tested on `python3.6` and above):

```
$ python -m pip install fwhunt-scan
```

Install manually:

```
$ git clone https://github.com/binarly-io/fwhunt-scan.git && cd fwhunt_scan
$ python setup.py install
```

# Example

### With script

Analyze/scan separate module:

```
$ python3 fwhunt_scan_analyzer.py analyze-image {image_path} -o out.json
$ python3 fwhunt_scan_analyzer.py scan --rule {rule_path} {image_path}
```

Scan the entire firmware image:

```
$ python3 fwhunt_scan_analyzer.py scan-firmware -r rules/BRLY-2021-001.yml -r rules/BRLY-2021-004.yml -r rules/RsbStuffingCheck.yml test/fw.bin
```

### With docker

To avoid installing dependencies, you can use the docker image.

You can build a docker image locally as follows:

```
docker build -t fwhunt_scan .
```

Example of use:

```
docker run --rm -it -v {module_path}:/tmp/image:ro \
  fwhunt_scan analyze-image /tmp/image # to analyze EFI module

docker run --rm -it -v {module_path}:/tmp/image:ro -v {rule_path}:/tmp/rule.yml:ro \
  fwhunt_scan scan /tmp/image -r /tmp/rule.yml # to scan EFI module with specified FwHunt rule

docker run --rm -it -v {module_path}:/tmp/image:ro -v {rule_path}:/tmp/rule.yml:ro \
  fwhunt_scan scan-firmware /tmp/image -r /tmp/rule.yml # to scan firmware image with specified FwHunt rule

docker run --rm -it -v {module_path}:/tmp/image:ro -v {rules_directory}:/tmp/rules:ro \
  fwhunt_scan scan-firmware /tmp/image --rules_dir /tmp/rules # to scan firmware image with specified rules directory
```

All these steps are automated in the `fwhunt_scan_docker.py` script:

```
python3 fwhunt_scan_docker.py analyze-image {module_path} # to analyze EFI module

python3 fwhunt_scan_docker.py scan -r {rule_path} {module_path} # to scan EFI module with specified FwHunt rule

python3 fwhunt_scan_docker.py scan-firmware -r {rule_path} {firmware_path} # to scan firmware image with specified FwHunt rule

python3 fwhunt_scan_docker.py scan-firmware --rules_dir {rules_directory} {firmware_path} # to scan firmware image with specified rules directory
```

### From code

#### UefiAnalyzer

Basic usage examples:

```python
from fwhunt_scan import UefiAnalyzer

...
uefi_analyzer = UefiAnalyzer(image_path=image_path)
print(uefi_analyzer.get_summary())
uefi_analyzer.close()
```

```python
from fwhunt_scan import UefiAnalyzer

...
with UefiAnalyzer(image_path=image_path) as uefi_analyzer:
    print(uefi_analyzer.get_summary())
```

On Linux platforms, you can pass blob for analysis instead of file:

```python
from fwhunt_scan import UefiAnalyzer

...
with UefiAnalyzer(blob=data) as uefi_analyzer:
    print(uefi_analyzer.get_summary())
```

#### UefiScanner

```python
from fwhunt_scan import UefiAnalyzer, UefiRule, UefiScanner

...
uefi_analyzer = UefiAnalyzer(image_path)

# rule1 and rule2 - contents of the rules on YAML format
uefi_rules = [UefiRule(rule1), UefiRule(rule2)]

scanner = UefiScanner(uefi_analyzer, uefi_rules)
result = scanner.result
```
