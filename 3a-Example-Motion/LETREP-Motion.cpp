//Required include files
#include <stdio.h>	
#include <string>
#include <iostream>
#include <chrono>
#include "C:/Program Files (x86)/Teknic/ClearView/sdk/inc/pubSysCls.h"	

using namespace sFnd;

// Send message and wait for newline
void msgUser(const char *msg) {
	std::cout << msg;
	getchar();
}

//*********************************************************************************
//This program will load configuration files onto each node connected to the port, then executes
//sequential repeated moves on each axis.
//*********************************************************************************
#define ACC_LIM_RPM_PER_SEC	6000
#define VEL_LIM_RPM			350
#define MOVE_DISTANCE_CNTS	3200
#define NUM_MOVES			5
#define TIME_TILL_TIMEOUT	10000	//The timeout used for homing(ms)

int main(int argc, char* argv[])
{/*
	msgUser("Motion Example starting. Press Enter to continue.");*/

	size_t portCount = 0;
	std::vector<std::string> comHubPorts;


	//Create the SysManager object. This object will coordinate actions among various ports
	// and within nodes. In this example we use this object to setup and open our port.
	SysManager* myMgr = SysManager::Instance();							//Create System Manager myMgr

	//This will try to open the port. If there is an error/exception during the port opening,
	//the code will jump to the catch loop where detailed information regarding the error will be displayed;
	//otherwise the catch loop is skipped over
	//try
	//{ 

	SysManager::FindComHubPorts(comHubPorts);
	//printf("Found %d SC Hubs\n", comHubPorts.size());

	for (portCount = 0; portCount < comHubPorts.size() && portCount < NET_CONTROLLER_MAX; portCount++) {

		myMgr->ComHubPort(portCount, comHubPorts[portCount].c_str()); 	//define the first SC Hub port (port 0) to be associated 
		// with COM portnum (as seen in device manager)
	}

	if (portCount < 0) {

		printf("Unable to locate SC hub port\n");

		msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key

		return -1;  //This terminates the main program
	}
	//printf("\n I will now open port \t%i \n \n", portnum);
	myMgr->PortsOpen(portCount);				//Open the port

	for (size_t i = 0; i < portCount; i++) {
		IPort& myPort = myMgr->Ports(i);

		//printf(" Port[%d]: state=%d, nodes=%d\n",
			//myPort.NetNumber(), myPort.OpenState(), myPort.NodeCount());



		//Once the code gets past this point, it can be assumed that the Port has been opened without issue
		//Now we can get a reference to our port object which we will use to access the node objects

		for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {
			// Create a shortcut reference for a node
			INode& theNode = myPort.Nodes(iNode);

			//theNode.EnableReq(false);				//Ensure Node is disabled before loading config file

			//myMgr->Delay(200);


			//theNode.Setup.ConfigLoad("Config File path");


			//printf("   Node[%d]: type=%d\n", int(iNode), theNode.Info.NodeType());
			//printf("            userID: %s\n", theNode.Info.UserID.Value());
			//printf("        FW version: %s\n", theNode.Info.FirmwareVersion.Value());
			//printf("          Serial #: %d\n", theNode.Info.SerialNumber.Value());
			//printf("             Model: %s\n", theNode.Info.Model.Value());

			//The following statements will attempt to enable the node.  First,
			// any shutdowns or NodeStops are cleared, finally the node is enabled
			//theNode.Status.AlertsClear();					//Clear Alerts on node 
			//theNode.Motion.NodeStopClear();	//Clear Nodestops on Node  				
			//theNode.EnableReq(true);					//Enable node 
			//At this point the node is enabled
			//printf("Node \t%zi enabled\n", iNode);
			double timeout = myMgr->TimeStampMsec() + TIME_TILL_TIMEOUT;	//define a timeout in case the node is unable to enable
			//This will loop checking on the Real time values of the node's Ready status
			while (!theNode.Motion.IsReady()) {
				if (myMgr->TimeStampMsec() > timeout) {
					printf("Error: Timed out waiting for Node %d to enable\n", iNode);
					msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
					return -2;
				}
			}

		}

		///////////////////////////////////////////////////////////////////////////////////////
		//At this point we will execute motion
		//////////////////////////////////////////////////////////////////////////////////////

		//msgUser("Motion Example starting. Press Enter to continue.");



		for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {
			// Create a shortcut reference for a node
			INode& theNode = myPort.Nodes(iNode);


			//Move Motor Up

			theNode.Motion.MoveWentDone();						//Clear the rising edge Move done register

			theNode.AccUnit(INode::RPM_PER_SEC);				//Set the units for Acceleration to RPM/SEC
			theNode.VelUnit(INode::RPM);						//Set the units for Velocity to RPM
			theNode.Motion.AccLimit = ACC_LIM_RPM_PER_SEC;		//Set Acceleration Limit (RPM/Sec)
			theNode.Motion.VelLimit = VEL_LIM_RPM;				//Set Velocity Limit (RPM)


			//printf("Moving Node \t%zi \n", iNode);
			//auto time = std::chrono::high_resolution_clock::now();
			auto time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
			theNode.Motion.MovePosnStart(-MOVE_DISTANCE_CNTS);			//Execute encoder count move 
			//printf("%f estimated time.\n", theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS));
			double timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 100;			//define a timeout in case the node is unable to enable

			while (!theNode.Motion.MoveIsDone()) {
				if (myMgr->TimeStampMsec() > timeout) {
					printf("Error: Timed out waiting for move to complete\n");
					msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
					return -2;
				}
			}
			//auto timeus = std::chrono::duration_cast<std::chrono::microseconds>(time);
			std::cout << time << std::endl;

			//printf("Node \t%zi Move Done\n", iNode);

			//msgUser("Motion Example starting. Press Enter to continue.");

			myMgr->Delay(1500);

			//move motor back to home

			theNode.Motion.MoveWentDone();						//Clear the rising edge Move done register

			theNode.Motion.VelLimit = 60;				//Set Downward Velocity Limit (RPM)


			//printf("Moving Node \t%zi \n", iNode);
			theNode.Motion.MovePosnStart(MOVE_DISTANCE_CNTS);			//Execute encoder count move 
			//printf("%f estimated time.\n", theNode.Motion.MovePosnDurationMsec(-MOVE_DISTANCE_CNTS));
			timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 100;			//define a timeout in case the node is unable to enable

			while (!theNode.Motion.MoveIsDone()) {
				if (myMgr->TimeStampMsec() > timeout) {
					printf("Error: Timed out waiting for move to complete\n");
					msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
					return -2;
				}
			}
			//printf("Node \t%zi Move Done\n", iNode);


		} // for each node






	//////////////////////////////////////////////////////////////////////////////////////////////
	//After moves have completed Disable node, and close ports
	//////////////////////////////////////////////////////////////////////////////////////////////
		//printf("Disabling nodes, and closing port\n");
		//Disable Nodes

	//	for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {
	//		// Create a shortcut reference for a node
	//		myPort.Nodes(iNode).EnableReq(false);
	//	}
	//}
////}
//catch (mnErr& theErr)
//{
//	printf("Failed to disable Nodes n\n");
//	//This statement will print the address of the error, the error code (defined by the mnErr class), 
//	//as well as the corresponding error message.
//	printf("Caught error: addr=%d, err=0x%08x\nmsg=%s\n", theErr.TheAddr, theErr.ErrorCode, theErr.ErrorMsg);

//	msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
//	return 0;  //This terminates the main program
//}

// Close down the ports
		myMgr->PortsClose();

		//msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
		return 0;			//End program
	}
}

