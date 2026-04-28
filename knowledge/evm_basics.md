# EVM and VVPAT Basics

The Indian election process relies heavily on technology to ensure secure, fast, and transparent voting. The two primary components are the Electronic Voting Machine (EVM) and the Voter Verifiable Paper Audit Trail (VVPAT).

## What is an EVM?

An Electronic Voting Machine (EVM) is a simple electronic device used to record votes. It consists of two main units:
1.  **Control Unit (CU)**: Kept with the Presiding Officer or a Polling Officer. It controls the entire voting process and stores the recorded votes.
2.  **Ballot Unit (BU)**: Placed inside the voting compartment. Voters use this unit to cast their vote by pressing a button next to their chosen candidate.

The two units are connected by a cable.

### Security Features of EVMs
*   **Standalone**: EVMs are standalone machines. They are not connected to the internet, Bluetooth, or any external network, making them immune to remote hacking.
*   **One Vote Limit**: Once a voter presses a button, the EVM locks and will not register another vote until the Control Unit is reactivated by the Polling Officer. This prevents multiple voting by a single person.
*   **Dynamic Coding**: Every press on the Ballot Unit generates a dynamic, encrypted code to the Control Unit, preventing tampering with the cable.

## What is a VVPAT?

The Voter Verifiable Paper Audit Trail (VVPAT) is an independent system attached to the EVM that allows voters to verify that their vote was cast as intended.

### How it Works
1.  When a voter presses a button on the Ballot Unit, the VVPAT machine prints a paper slip containing the serial number, name, and symbol of the chosen candidate.
2.  This slip is visible to the voter through a transparent glass window for about 7 seconds.
3.  After 7 seconds, the slip automatically cuts and falls into the sealed drop box of the VVPAT machine.
4.  The voter does not get to take the slip home.

### Purpose of VVPAT
*   **Verification**: It provides a physical paper trail for verification of the electronic votes.
*   **Dispute Resolution**: In case of a dispute or allegations of EVM malfunction, the VVPAT slips can be counted and tallied with the electronic count from the Control Unit to ensure accuracy.
