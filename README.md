# OKVED Phone Matcher

A small script that normalizes a Russian mobile phone number, downloads the up-to-date `okved.json` over HTTPS, and finds the OKVED code with the maximum suffix match.

---

## Code style and documentation

The code follows **PEP 8** for formatting and **PEP 257** for docstrings.

---

## Requirements

- Python **3.11+**
- Internet access

---

## Install dependencies

```
pip install requests
```
Run CMD
```
python main.py "<phone_number>"
```
Examples:
```
python main.py "8 (999) 123-45-55"
python main.py "+7 999 123 45 55"
python main.py "9991234555"
```
Output
```
+79991234555 # 
55
Деятельность по предоставлению мест для временного проживания
2
```

- Normalized phone number 
- OKVED code
- OKVED name
- Suffix match length

Errors

- Invalid phone number: 
```
false: Invalid phone number
```

- No OKVED match found:
```
false: Phone number doesn't have matches
```
