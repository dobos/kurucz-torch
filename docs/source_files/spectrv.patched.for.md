# SPECRV

Purpose: Computes the synthetic spectrum

Compiled from: ./src/spectrv.patched.for

Executed in: synthe_{n} subdirectory

Executed as:

```
# spectrv.exe computes the synthetic spectrum
ln -s {s_files}/molecules.dat fort.2
cat <<"EOF" >fort.25
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
EOF
{synthe_suite}/spectrv.exe<"{synthe_solar}">spectrv.out

mv fort.7 spectrum.bin
# rm fort.*
# rm xnfpelsyn.dat
```

## Interface

Input:

* fort.25: 

Output:

* stdout > spectrv.out

## Subroutines

None

### READIN(MODE)

atlas7v.for:1326

Parameters
----------

* MODE
    * MODE=1 COMPUTE A MODEL
    * MODE=2 READ A PREVIOUSLY CALCULATED MODEL FOR SOME APPLICATION
    * MODE=20 SAME AS 2 BUT ON ENCOUNTERING END RETURN WITH NRHOX=0



## Function calls

### READIN(20)
spectrv.patched.for:130 -> atlas7v.for:1326

MODE=20: READ A PREVIOUSLY CALCULATED MODEL FOR SOME APPLICATION BUT ON
ENCOUNTERING END RETURN WITH NRHOX=0

### JOSH()

### CORINT()

### LINCEN()