# PQC in TLS

Mit Hilfe dieses Projekts sollen verschiedene PQC Algorithmen für Schlüsselaustausch und Authentifizierung auf ihre Performanz hin evaluiert werden. Dazu werden die Algorithmen in TLS 1.3  integriert und anhand eines Frameworks des Linux Kernels zur Netzwerkemulation getestet.

## Wichtige Komponenten

### Open Quantum Save
Das [Open Quantum Save (OQS)](https://github.com/open-quantum-safe)  ist ein open source Projekt, welches die Entwicklung und Intergration von PQC Techniken unterstützen soll. Es beinhaltet unter anderem verschiedene Implementierungen für die PQC Kandidaten des [NIST](https://www.nist.gov) [Standardisierungsprozesses](https://csrc.nist.gov/projects/post-quantum-cryptography).

#### OpenSLL
[OQS-OpenSSL](https://github.com/open-quantum-safe/openssl) ist im OQS Projekt verankert und bietet eine open source Bibliothek für die Verwendung von TLS 1.3 mit PQC Algorithmen. 

### PQ TLS Benchmark Framework
Dieses [Benchmarking Framework](https://github.com/xvzcf/pq-tls-benchmark) wurde in einem [Paper von Christian Paquin, Douglas Stebila, and Goutam Tamvada](https://eprint.iacr.org/2019/1447) in 2019 beschrieben und dient der Evaluierung von PQC Algorithmen in TLS 1.3. Für eine realistische Netzwerk Emulation wird hierzu das Linux Kernel Tool [netem](https://www.linux.org/docs/man8/tc-netem.html) genutzt, um somit Phänomene wie Paketverlust zu simulieren. Zum Vergleich wurden zudem Experimente in realer Umgung durchgeführt. Hierbei wurden Server in den USA, EU, und Australien genutzt, um TLS 1.3 Verbindungen mittels PQC Algorithmen aufzubauen. das Framework ist als Open Source Projekt frei verfpgbar und soll in diesem Projekt genutzt und weiter entwickelt werden, um weitere PQC Algorithmen und Konfigurationen zu evaluieren.

## Anforderungen an die Testumgebung
* Ubuntu (18.04+)
* Linux Kernel (4.12+)
* Für die Nutzung der PQC Algorithmen innerhalb von liboqs ist die CPU-Unterstützung folgender Erweiterungen notwendig
    > avx2
    > bmi1
    > bmi2
    > popcnt
    > sse2

## Installation
Sofern die oben beschrieben Bedingungen erfüllt sind, kann die Installation aller notwendigen Komponenten anhand des Skripts [install-prereqs-ubuntu.sh](https://code.fbi.h-da.de/aw/prj/athenepqc/pqc-in-tls/-/blob/all_algorithms2/pq-tls-benchmark-framework/emulation-exp/code/install-prereqs-ubuntu.sh) erfolgen.

## Experimente
Für die Experimente muss der Ordner 'pq-tls-benchmark-framework/emulation-exp/code/kex' aufgesucht werden. Anschließend kann das Skript [run.sh](https://code.fbi.h-da.de/aw/prj/athenepqc/pqc-in-tls/-/blob/all_algorithms2/pq-tls-benchmark-framework/emulation-exp/code/kex/scripts/run.sh) aufgerufen werden.
