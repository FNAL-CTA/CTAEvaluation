[//]: # (Please maintain the convention of one sentence per line. This makes change tracking easier in git.)

Ten Percent CMS CTA Testbed
===========================

As a step towards a migration of the production CMS and Public Enstore installations, we are planning a testbed with 10% of the throughput of the CMS Enstore system.
The total capacity will probably be a few percent of the CMS Enstore system.
This testbed will allow us to test and refine the migration procedure, gain operational experience with CTA, and perform some performance and acceptance tests.
It will also allow us to develop the monitoring dashboards to be used for the full setup. 

We aim to complete this setup during CY 2023.

## Indentifying Resources

### Library 

The IBM TS4500G1 library is easily partitioned; we are currently using a small partition now for CTA testing. 
A partition of this library with tape drives and decommisioned tapes will form the basis of the 10% testbed.

### Tapes

There are several hundred Enstore M8 tapes with only deleted CMS data on them.
A portion of these tapes will be migrated to test the migration procedure and reading Enstore tapes.
The remainder will be made available to be re-written as CTA tapes for native performance tests. 

### Tape drives

Between its two robots, the CMS libraries have 76 tape drives available. 
For a 10% test, eight tape drives (LTO-8) will be placed into a logical library in the IBM system. 
If CMS wishes to use the 10% test to partake in the 2024 WLCG data challenge, moving additional drives into the test system may be required.
See the section on tests for more information.
Each tape drive has a theortical read/write speed of 400 MB/s; the eight drives will have a theoretical max of 3.2 GB/s.

### EOS buffer servers and space

The initial tape buffer will be based on EOS, following the CERN setup. 
We anticipate a followup testbed with dCache as the buffer space used to inform our decision on the filesystem to use.

There are NVME systems with 48 TB each which can be used for this purpose; we would like to use two or three of these as FST nodes.
We assume these machines are 16x3 TB NVME disks. 
This is approximately the size of the tape buffer "building blocks" that CERN uses in its CTA systems. 
CERN recommends a minimum of 3 nodes for QuarkDB (QDB).
For large VOs, we believe CERN uses multiples of these building blocks to provide enough SSD bandwidth to feed the required number of tape drives.

The recommended setup for a EOS buffer is
- Two or three machines with 48 TB NVMe  (this will give 6 or 9 GB/s bandwidth according to CERN)
  - Each will run the EOS FST and QDB
  - 45 TB dedicated to the FST
  - 3 TB dedicated to the QDB storage and/or system disk
  - At least 8 cores and 64 GB of RAM
- A dedicated node for EOS MGM
  - Will also run QDB if only two FST nodes are provided
  - At least 8 cores, 64 GB of RAM
  - At least 1 TB of SSD for system disk and QDB storage

This buffer may be somewhat larger than the 10% of a full production scale system, however 6 GB/s of IO capacity matches well with 3.2 GB/s to/from tape plus an equal amount to/from the LAN or WAN.
This property makes a deployment of this size a good fit for our system, which targets specifically 10% tape throughput.


### CTA nodes

#### Frontend(s)

The frontend is the CTA node which takes requests from the client code and put requests in the CTA queues.
It is also responsible for returning information to user queuries (`cta-admin-*` commands).
Currently this is service runs on `storagedev201.fnal.gov`.
This may either be hosted in OKD (see Use of containers below) or a dedicated node.
If a dedicated node is needed, a typical farm node should suffice.

#### Tape Servers 

Tape servers (movers in Enstore parlance) are responsible for managing tape drives. 
These run two daemons: `taped`, which is responsible for reading and writing from disk and tape; 
and `rmcd`, which is responsible for issuing mount requests. 
These are nodes currently attached to the LTO-8 tape drives we will use.

#### Use of containers

We will explore virtualization technologies to make setup and installation of the CTA-specific infrastructure fast and reproducible.
We expect to use `docker` or `podman` containers, `kubernetes`, and `helm` charts for these deployments.
We currently envision using the FNAL OKD cluster for the frontend, the PostgreSQL queue database, and the monitoring tied to the frontend.
On the tape server nodes, it may be necessary to use one container per tape drive to mimic CERN's one drive per machine setup.
On the tape servers, we expect to deploy the monitoring in a virtualized environment running in kubernetes on the machine.

### Object store

We hope that by the time CTA is used in production for Fermilab, the object store used for queueing will be replaced by a PostgreSQL implementation.
For the 10% test we will still need to use the Ceph installation as an object store.
The existing Ceph installation is not yet highly utilized, and offers plenty of storage space and I/O bandwidth to service our 10% test instance.
The CTA evaluation instance is currently using this Ceph installation.

### Staging space (if needed)

The CTA team at CERN are strong proponents of using an on-site disk area as staging space for files destined for or coming from tape.
At CERN, this takes the form of a large disk pool; at Fermilab we will use the CMS dCache area if needed.
The driver behind this is that, to supply enough bandwidth to feed all the tape drives at the 400 MB/s theoretical maximum write speed, one either needs a very large disk pool or a smaller SSD pool. 
Having chosen the smaller SSD pool, one then needs additional space to buffer the many transfers coming from off-site. 
Once a copy of a file is completely on site, then it can be moved to the fast buffer before being written to tape. FTS and/or Rucio can be used to appropriately throttle these transfers.
To minimize the need for staging space, we can initially ensure that only data from `T1_US_FNAL_Disk` is sent to CTA and vice versa.

### FTS server(s)

We will use the CMS FTS3 service based at Fermilab to manage jobs writing to the CTA testbed.
Being a production scale service, this service will be more than capable of providing the bandwidth necessary to hit our 10% tape throughput goal.

### Database servers

The current CTA test database is on servers managed by the Database Services group in ITD. 
We expect that to continue to be the case for the production database. 
The size is not expected to be very large (few kB/file).

When CTA transitions to a PostgreSQL database instead of Ceph for its internal queueing, that will be a separate database.
The queueing database will likely be hosted in the cluster.

### Management of required nodes

We need to define Puppet zones for the various CTA and EOS nodes. We hope to place these under management by SSI.
They will include at least a custom firewall configuration for our service, as well as boilerplate monitoring infrastructure for all servers.
We hope to also include configuration that allows us to deploy homogenous containerization infrastructure, particularly on tape server nodes, to simplify Kubernetes setup.

## Migrating Enstore Metadata to EOS/CTA

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
This uses a docker container built expressly for this purpose with the right combination of python, libraries, and CTA RPMs. 
It's currently based on CentOS7 but we will move to Alma9 when CTA RPMs become available there.
Checking for EOS directories and files is done with EOS commands. 
This is the slowest part of the process, but is also a good candidate for improvement using `eossh` scripts.
This improvement is currently written, but not tested.
Tape descriptions in CSV or Enstore PostgreSQL are translated to CTA PostgreSQL in Python using SQLAlchemy.
Making EOS placeholder files and modifying the CTA database is done with a CTA executable, `cta-eos-namespace-inject`.

## Rucio setup

We will set up the 10% testbed as a new Rucio RSE named `T1_US_FNAL_Tape_Test` first in the Rucio integration testbed, and later in the production Rucio system.
Data will be registered, for the CTA testbed, in Rucio as was done during the PhEDEx to Rucio migration in CMS.
Using the unidirectional `distances` of Rucio, we can keep the CTA testbed from being used as a source of data.
An open question is whether `T1_US_FNAL_Tape_Test` will eventually become `T1_US_FNAL_Tape` or if the CTA migration process will be done under the hood without Rucio's knowledge or involvement.
The feasibility and experience of other sites who have performed storage system migrations will be considered when making this decision.

## Plan for backups

A plan for backing up CTA and EOS (and/or dCache namespace data) will be formulated. 
This must be done for the CTA database as well as for the EOS or dCache namespace information. 
This is especially critical since the namespace is not in the CTA database (unlike Enstore).

## Monitoring plan

All monitoring data collected from CTA will be sent to Fermilab Landscape. 
Current plans call for state information to be collected from `cta-admin` commands and performance information to be collected from log files on various nodes.
The monitoring collection infrastructure will be hosted in containers (and likely Kubernetes) on the nodes where it is needed to simplify deployment.
Dashboards, collected from other CTA institutions and new dashboards to replicate necessary monitoring from Enstore, will be developed in collaboration with the tape operations group.

We will use fluentd in a docker container to bring log information from the cta node and the tape node to Kafka. 
We are going to collect information from cta-taped on the tape node, this we are calling performance information.
On the CTA tape node, specifically, the messages "tape read successfully" and "file successful read" will be used. 
We will read out the tape load times, unmount time, positioning time, the drive transfer time, and the total time the event takes.
On the CTA node we will collect information from CTA-admin commands including tape information (tape identification, average volume per retrieve and archive tape mount), failed requests, show queues, and bytes transferred.

This monitoring data will be compared with throughput and load data from EOS and FTS, as well as hardware load monitoring.
These sources, taken together, should allow us to form reasonable predictions about resource requirements and theoretical load at production scale.

## Tests to be done

We envision a series of tests to be performed with this testbed.

1. Basic read and write tests. We have done these on the test installation already but they should be repeated.
   1. Read tests should include both sequential (whole tape) reads of both Enstore and CTA tapes and sparse reads, also from Enstore and CTA tapes
2. Multiple simultaneous reads and writes. What is the aggregate performance of the testbed system while all tape drives are being exercised?
3. Single vs. dual tape drives per mover node. 
Concern has been expressed by the CTA team at CERN that we may pay a performance penalty by staying with our current setup of two drives per mover node. 
We should determine if this is true and quantify it, if so.
4. Simulated CMS workflows.
We will recall CMS datasets in a similar manner to the CMS production system noting time, rates, and number of mounts per file.
We will compare this with the performance of Enstore to the exent possible.
4. Explore the parameters for waiting to write tapes (how much space do we need/file to write). 
We will document our findings.

### WLCG data challenge – March 2024

WLCG and CMS have scheduled a data challenge for early 2024 before data taking resumes. 
The goal is to be a 25% test of the HL-LHC needs. 
This implies 100 Gb/s of data flow into Fermilab which, in turn, implies about 30 tape drives writing at maximum speed if we want to keep up with writing the incoming data to tape.

This  test will be done with CTA, either with the 10% test or with Enstore fully migrated to CTA.
If it is done with the 10% test, it may be necessary to temporarily move additional tape drives into the 10% test to keep up with incoming data flows.


[//]: # (![SFA dagram]&#40;SFA.png&#41;)

[//]: # (*A diagram of the existing SFA process in Enstore/dCache*)

## Personnel 

The following people will be involved: Ren Bauer, Leo Munoz, Scarlet Norberg, Dan Szokla, Eric Vaandering

## Notes
