//******************************************************************
//Required include files & namespace
//******************************************************************

#include <stdio.h>      
#include <string>
#include "C:/Program Files (x86)/Teknic/ClearView/sdk/inc/pubSysCls.h"
#include <iostream>


using namespace sFnd;




// *****************************************************************
// Function to send message and wait for newline
// *****************************************************************


void msgUser(const char* msg) {
	std::cout << msg;
	getchar();
}




//*********************************************************************************
// Definitions for motion limits
//*********************************************************************************

#define ACC_LIM_RPM_PER_SEC		1000
#define VEL_LIM_RPM		30
#define MOVE_DISTANCE_CNTS	15990
#define NUM_MOVES			5
#define TIME_TILL_TIMEOUT	10000
//The timeout used for homing(ms)



//*********************************************************************************
// Function to move motion
//*********************************************************************************

int main(int argc, char* argv[])
{
	double mytrq = 0;
	//Declare torque variable
	msgUser("Motor Testing starting. Press Enter to continue.");

	size_t portCount = 0;
	std::vector<std::string> comHubPorts;


	//Create the SysManager object to coordinate actions among various ports and within nodes
	SysManager* myMgr = SysManager::Instance();
	//Create System Manager myMgr




	//*********************************************************************************
	// Attempt to connect to ports and nodes
	//*********************************************************************************

	try
	{

		SysManager::FindComHubPorts(comHubPorts);
		printf("Found %d SC Hubs\n", comHubPorts.size());

		for (portCount = 0; portCount < comHubPorts.size() && portCount < NET_CONTROLLER_MAX; portCount++) {

			myMgr->ComHubPort(portCount, comHubPorts[portCount].c_str());
			//define SC Hub port 0 to be associated with COM portnum
		}

		if (portCount < 0) {

			printf("Unable to locate SC hub port\n");

			msgUser("Press any key to continue.");

			return -1;  //This terminates the main program
		}


		myMgr->PortsOpen(portCount);
		//Open the port



		for (size_t i = 0; i < portCount; i++) {
			IPort& myPort = myMgr->Ports(i);


			// Get reference to ports for access to nodes

			for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {

				INode& theNode = myPort.Nodes(iNode);
				// Create a shortcut reference for a node

				theNode.EnableReq(false);
				//Ensure Node is disabled before loading config file


				// Enable nodes

				theNode.Status.AlertsClear();
				//Clear Alerts on node
				theNode.Motion.NodeStopClear();
				//Clear Nodestops on Node                       
				theNode.EnableReq(true);
				//Enable node



				double timeout = myMgr->TimeStampMsec() + TIME_TILL_TIMEOUT;
				//Check for timeout                                         
				while (!theNode.Motion.IsReady()) {
					if (myMgr->TimeStampMsec() > timeout) {
						printf("Error: Timed out waiting for Node %d to enable\n", iNode);
						msgUser("Press any key to continue.");
						return -2;
					}
				}


			//*********************************************************************************
			// Homing Process
			//*********************************************************************************

			msgUser("Home Motion starting. Press Enter to continue.");

			if (theNode.Motion.Homing.HomingValid())
				//Check if homing configs are valid
			{


				if (theNode.Motion.Homing.WasHomed())
					//Check if node has been homed
				{
					printf("Node %d has already been homed, current position is: \t%8.0f \n", iNode, theNode.Motion.PosnMeasured.Value());
					printf("Rehoming Node... \n");
				}
				else
				{
					printf("Node [%d] has not been homed.  Homing Node now...\n", iNode);
				}


				theNode.Motion.Homing.Initiate();
				//Home the node


				timeout = myMgr->TimeStampMsec() + TIME_TILL_TIMEOUT;
				//Check for timeout
				while (!theNode.Motion.Homing.WasHomed()) {
					if (myMgr->TimeStampMsec() > timeout) {
						printf("Node did not complete homing:  \n\t -Ensure Homing settings have been defined through ClearView. \n\t -Check for alerts/Shutdowns \n\t -Ensure timeout is longer than the longest possible homing move.\n");
						msgUser("Press any key to continue.");
						return -2;
					}
				}


				printf("Node completed homing\n");
			}

			else {
				printf("Node[%d] has not had homing setup through ClearView.  The node will not be homed.\n", iNode);
			}


		}





			//*********************************************************************************
			// Motion Process
			//*********************************************************************************

			msgUser("Fire Motion starting. Press Enter to continue.");


			for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {
				// Create a shortcut reference for a node
				INode& theNode = myPort.Nodes(iNode);

				for (int speedCom = 3900; speedCom < 3992; speedCom += 10) {


					//Move Motor Up

					theNode.Motion.MoveWentDone();
					//Clear the rising edge Move done register

					theNode.AccUnit(INode::RPM_PER_SEC);
					//Set the units for Acceleration to RPM/SEC
					theNode.VelUnit(INode::RPM);
					//Set the units for Velocity to RPM
					theNode.Motion.AccLimit = 99900000;
					//Set Acceleration Limit (RPM/Sec)
					theNode.Motion.VelLimit = speedCom;
					//Set Velocity Limit (RPM)


					//printf("Moving Node \t%zi \n", iNode);

					// ***************************************************************
					// Real Motion File Has Timing Here
					// ***************************************************************


					double speed1 = 0;
					double speed2 = 0;
					theNode.Motion.MovePosnStart(1600);
					//Execute encoder count move
					speed1 = myMgr->TimeStampMsec();
					//printf("%d estimated time.\n", theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS));
					//double timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 1000;             //define a timeout in case the node is unable to enable

					while (!theNode.Motion.MoveIsDone()) {
						theNode.Motion.VelMeasured.Refresh();
						//theNode.Motion.TrqMeasured.Refresh();
						//printf("%lg\n", double(theNode.Motion.TrqMeasured));
						//printf("%lg\n", double(theNode.Motion.VelMeasured));
						if (double(theNode.Motion.VelMeasured) < 0) {
							break;
						}
						//if (myMgr->TimeStampMsec() > timeout) {
						//    printf("Error: Timed out waiting for move to complete\n");
						//    msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
						//    return -2;
						//}
					}
					speed2 = myMgr->TimeStampMsec();


					//printf("Node \t%zi Move Done\n", iNode);

					printf("%lg\n", (speed2 - speed1));

					//printf("%lg\n", double(theNode.Motion.VelMeasured));

					//msgUser("Move down. Press Enter to continue.");


					//move motor back to home

					myMgr->Delay(1500);

					theNode.Motion.MoveWentDone();
					//Clear the rising edge Move done register

					theNode.Motion.VelLimit = 60;
					//Set Downward Velocity Limit (RPM)


					//printf("Moving Node \t%zi \n", iNode);
					theNode.Motion.MovePosnStart(-1600);
					//Execute encoder count move
					//printf("%f estimated time.\n", theNode.Motion.MovePosnDurationMsec(-MOVE_DISTANCE_CNTS));
					//timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 100;               //define a timeout in case the node is unable to enable

					while (!theNode.Motion.MoveIsDone()) {
						//if (myMgr->TimeStampMsec() > timeout) {
						//    printf("Error: Timed out waiting for move to complete\n");
						//    msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
						//    return -2;
						//}
					}

					myMgr->Delay(500);
					//printf("Node \t%zi Move Done\n", iNode);
				}

			} // for each node



	  //////////////////////////////////////////////////////////////////////////////////////////////
	  //After moves have completed Disable node, and close ports
	  //////////////////////////////////////////////////////////////////////////////////////////////
			printf("Disabling nodes, and closing port\n");
			//Disable Nodes

			for (size_t iNode = 0; iNode < myPort.NodeCount(); iNode++) {
				// Create a shortcut reference for a node
				myPort.Nodes(iNode).EnableReq(false);
			}
		}
	}
	catch (mnErr& theErr)
	{
		printf("Failed to disable Nodes n\n");
		//This statement will print the address of the error, the error code (defined by the mnErr class),
		//as well as the corresponding error message.
		printf("Caught error: addr=%d, err=0x%08x\nmsg=%s\n", theErr.TheAddr, theErr.ErrorCode, theErr.ErrorMsg);

		msgUser("Press any key to continue."); //pause so the user can see the error message; waits for user to press a key
		return 0;  //This terminates the main program
	}

	// Close down the ports
	myMgr->PortsClose();

	msgUser("Press any key to continue.");
	//pause so the user can see the error message; waits for user to press a key
	return 0;
	//End program
}