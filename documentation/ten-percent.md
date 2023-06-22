[//]: # (Please maintain the convention of one sentence per line. This makes change tracking easier in git.)

Ten Percent CMS CTA Testbed
===========================

As a step towards a migration of the production CMS and Public Enstore installations, we are planning a 10% testbed.
This testbed will allow us to test and refine the migration procedure, gain operational experience with CTA, and perform some performance and acceptance tests.
It will also allow us to develop the monitoring dashboards to be used for the full setup. 

We aim to complete this setup during CY 2023.

## Indentifying Resources

### Tapes

There are several hundred Enstore M8 tapes with only deleted CMS data on them.
A portion of these tapes will be migrated to test the migration procedure and reading Enstore tapes.
The remainder will be made available to be re-written as CTA tapes for performance tests. 

### Tape drives

Between its two robots, the CMS libraries have 70(?) tape drives available. 
For a 10% test, eight tape drive should be placed into a logical library in the IBM system, which is easy to partitions. 
If CMS wishes to use the 10% test to partake in the 2024 WLCG data challenge, moving additional drives into the test system may be required.
See the section on tests for more information.

### Buffer servers and space

The initial tape buffer will be based on EOS, following the CERN setup. 
We anticipate a followup testbed with dCache as the buffer space used to inform our decision on the filesystem to use.

There are three NVME systems with 48 TB each which can be used for this purpose. 
This is approximately the size of the tape buffer "building blocks" that CERN uses in its CTA systems.
For large VOs, we believe CERN uses multiples of these building blocks to provide enough SSD bandwidth to feed the required nuber of tape drives.

### Object store

We hope that by the time CTA is used in production for Fermilab, the object store used for queueing will be replaced by a PostgreSQL implementation.
For the 10% test we will still need to use the Ceph installation as an object store.
The CTA evaluation instance is currently using this Ceph installation.

### Staging space (if needed)

The CTA team at CERN are strong proponents of using an on-site disk area as staging space for files destined for or coming from tape.
At CERN, this takes the form of a large disk pool; at Fermilab we will use the CMS dCache area if needed.
The driver behind this is that to supply enough bandwidth to feed all the tape drives at the 400 MB/s theoretical maximum write speed, one either needs a very large disk pool or a smaller SSD pool. 
Having chosen the smaller SSD pool, one then needs additional space to buffer the many transfers coming in from off-site. 
Once a copy of a file is completely on site, then it can be moved to the fast buffer before being written to tape. FTS and/or Rucio can be used to appropriately throttle these transfers.

### FTS server(s)

We will use the CMS FTS3 server based at Fermilab to manage jobs writing to the CTA testbed.

## Migrating Enstore Metdata to EOS/CTA

Note that one difference between Enstore and CTA is that Enstore maintains the name of files while CTA does not. 
CTA relies on EOS to store the namespace.

Several tapes worth of data have been successfully migrated into CTA. 
These are decommissioned Enstore tapes, similar to those which will populate the 10% system.
Migration proceeds in several steps using a few different tools:
- Create directories and check for already existing EOS files
- Copy Enstore metadata into CTA database tables. 
This can be done from two sources; the CSV source is the most used now since these tapes no longer have any information in Enstore. 
  1. CSV files containing all the relevant information from Enstore
  2. The Enstore database using existing SQL models 
- Make placeholder files in EOS
  - These files have a size, a checksum, and are noted as "one tape copy, zero disk copies."
- Connect the CTA and EOS representations of the files. **This connection is bidirectional**. 

This entire process is driven by Python with executions of other EOS and CTA commands in subprocesses.
Checking for EOS directories and files is done with EOS commands. 
This is the slowest part of the process, but is also a good candidate for improvement using `eossh` scripts.
Tape descriptions in CSV or Enstore PostgreSQL to CTA PostgreSQL data is translated by Python using SQLAlchemy.
Making EOS placeholder files and modifying the CTA database is done with a CTA executable, `cta-eos-namespace-inject`.

## Rucio setup

We will set up the 10% testbed as a new Rucio RSE named `T1_US_FNAL_Tape_Test` first in the Rucio integration testbed and later in the production Rucio system.
Data will be registered, for the CTA testbed, in Rucio as was done during the PhEDEx to Rucio migration in CMS.
An open question is whether `T1_US_FNAL_Tape_Test` will eventually become `T1_US_FNAL_Tape` or if the CTA migration process will be done under the hood without Rucio's knowledge or involvement.
The feasibility and experience of other sites who have performed storage system migrations will be considered when making this decision.

## Monitoring plan

All monitoring data collected from CTA will be sent to Fermilab Landscape. 
Current plans call for state information to be collected from `cta-admin` commands and performance information to be collected from log files on various nodes.
The monitoring collection infrastructure will be hosted in containers (and likely Kubernetes) on the nodes where it is needed to simplify deployment.
Dashboards, collected from other CTA institutions and new dashboards to replicate necessary monitoring from Enstore, will be developed in collaboration with the tape operations group.

We will use fluentd in a docker container to bring log information from the cta node and the tape node to kafka. We are going to collect information from cta-taped on the tape node, this we are calling performance information.
On the CTA tape node messages from tape read successfully and file successful read will be used. We will read out the tape load times, unmount time, positioning time, the drive transfer time, the total time the event takes,
On the CTA node we will collect information from CTA-Admin commands including tape information (tape identification, average volume per retrieve and archive tape mount), failed requests, show queues, bytes transferred.

## Tests to be done

We envision a series of tests to be performed with this testbed.

1. Basic read and write tests. We have done these on the test installation already but they should be repeated.
   1. Read tests should include both sequential (whole tape) reads of both Enstore and CTA tapes and sparse reads, also from Enstore and CTA tapes
2. Multiple simultaneous reads and writes. What is the aggregate performance of the testbed system while all tape drives are being exercised?
3. Single vs. dual tape drives per mover node. 
Concern has been expressed by the CTA team at CERN that we may pay a performance penalty by staying with our current setup of two drives per mover node. 
We should determine if this is true and quantify it, if so.

### WLCG data challenge – March 2024

WLCG and CMS have scheduled a data challenge for early 2024 before data taking resumes. 
The goal is to be a 25% test of the HL-LHC needs. 
This implies 100 Gb/s of data flow into Fermilab which, in turn, implies about 30 tape drives writing at maximum speed if we want to keep up with writing the incoming data to tape.

This  test will be done with CTA, either with the 10% test or with Enstore fully migrated to CTA.
If it is done with the 10% test, it may be necessary to temporarily move additional tape drives into the 10% test to keep up with incoming data flows.


[//]: # (![SFA dagram]&#40;SFA.png&#41;)

[//]: # (*A diagram of the existing SFA process in Enstore/dCache*)
