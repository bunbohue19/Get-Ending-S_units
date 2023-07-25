# Get-Ending-S_units

To initiate, get requirement in conda:

```
pip install -r requirement.txt
```python

To generate sunit extraction from java files to java file, input file must not contain class or packages, only 1 method. For quick start:

```
import Hung.extractSunit
input="input_java_file.java"
output="output_java_file.java"
extract(input,output)
```python

For generate sunit extraction from text to text:

```
from methodCFG import Sunit
java_method="your java method" #your java method
sunit=Sunit(java_method)
sunit.composeSunit()
print(sunit.source_code)

```python
