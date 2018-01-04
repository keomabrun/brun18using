# Reviewer 1

The main issue of the paper is the organization and presentation. The manuscript is organized and presented more as a technical report than a scientific paper.
Specifically, it lacks of a section providing a technical background and an analysis of the related work.
The introduction does not properly introduce the context of the research.
The adopted solution, the SmartMesh IP, is presented only from a high level, if possible it should be presented more in details.

## Other (minor) issue
- The authors mention that the SmartMesh IP exploits multi-hop communication. How is that achieved? Is the RPL protocol exploited?

- In Section 4.1 the authors state that "Fig.6 shows that the RSSI difference never exceeds a couple od dB.". From Fig.6(b) looks that in some cases that happen. Can the authors comment further on that? Could the link symmetry highlighted in these results guaranteed by TSCH channel hopping?


# Reviewer 2

First, the SmartMesh IP technology should be detailed. Second the authors must present the state-of-the-art concerning (i) other experimental initiatives in the area and/or (ii) other technologies similar to SmartMesh IP to justify the use of this technology.
The authors should explain “what is” the SmartMesh IP technology. Is this a “new” network architecture? Which layers does it implements? It also implements the monitoring application? All these questions are emerged from the third paragraph of Section 2.

The authors state that ‘Several wireless technologies operate in the same building, including Wi-Fi, Bluetooth and other IEEE802.15.4-based networks. “ How difficult is to produce a heat map of the environment to support the results presented in Section 3.2?

The authors should also clarify the process of adding nodes to the network. How the handshake is started? Messages are exchanged between the new node and the SmartMesh IP manager throuhg multihop communication? In addition, nodes send `HR_*` messages to gateway periodically or store these messages locally? Please provide more details about these issues in Section 2.

I understand the use of Friis transmission model in the agriculture use case but I am not convinced the use of this model in the smart building environment is appropriate. I also do not understand why -40 dB is a reasonable value to adjust the model. Please discuss these points in the first paragraph of Section 3.1.

Please provide more details about the data and control traffic in Section 3.3., i.e., the size of data and control messages, the time interval between messages or the transmission rate, if the both messages – data and control -- are considered to compute losses. With these details in mind, readers can estimate the network throughput, for example.

How does the criteria adopted by SmartMesh IP to infer a bad link (Section 3.2) impacts stability? I believe this criteria is the main reason for the results obtained in Section 4.2.
