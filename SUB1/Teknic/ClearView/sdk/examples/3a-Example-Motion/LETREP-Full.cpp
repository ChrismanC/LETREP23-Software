//Required include files
#include <stdio.h>	
#include <string>
#include <iostream>
#include "C:/Program Files (x86)/Teknic/ClearView/sdk/inc/pubSysCls.h"
#include <windows.h>
#include <chrono>
//need windows.h for pipes!


using namespace sFnd;


// Send message and wait for newline
void msgUser(const char* msg) {
	std::cout << msg;
	getchar();
}

//this sends given data to a given pipe like so:
//  sendData(pipe, result, L"1"); sends 1 through the pipe, encoded in bytes as ASCII
//for variables, use swprintf_s
// wchar_t word[17];
// swprintf_s(word, 17, L"%f", theTrq);
// sendData(toPy, result, word);
void sendData(HANDLE pipe, BOOL result, const wchar_t* data) {

	// wcout << "Sending data to pipe..." << endl;

	// This call blocks until a client process reads all the data
	//const wchar_t *data = L"*** Hello Pipe World ***";	//original

	DWORD numBytesWritten = 0;
	result = WriteFile(
		pipe, // handle to our outbound pipe
		data, // data to send
		wcslen(data) * sizeof(wchar_t), // length of data to send (bytes)
		&numBytesWritten, // will store actual amount of data sent
		NULL // not using overlapped IO
	);


	/*if (result) {
		wcout << "Number of bytes sent: " << numBytesWritten << endl;
	}
	else {
		wcout << "Failed to send data." << endl;
		// look up error code here using GetLastError()
	}*/
	//Sleep(2000);
}


//*********************************************************************************
//This program will load configuration files onto each node connected to the port, then executes
//sequential repeated moves on each axis.
//*********************************************************************************

#define ACC_LIM_RPM_PER_SEC	99900000
#define VEL_LIM_RPM			30
#define MOVE_DISTANCE_CNTS	1200
#define TIME_TILL_TIMEOUT	10000	//The timeout used for homing(ms)


int main(int argc, char* argv[])
{
	double theTrq;

	size_t portCount = 1;
	std::vector<std::string> comHubPorts;

	SysManager* myMgr = SysManager::Instance();

	//Find and label ports
	SysManager::FindComHubPorts(comHubPorts);

	if (comHubPorts.size() != 1) {
		/* ********************************************************************************************
			Pipe ERROR or just let it figure out C failed and closed
		********************************************************************************************** */
		return -1;
	}

	myMgr->ComHubPort(0, comHubPorts[0].c_str());
	myMgr->PortsOpen(portCount);
	IPort& myPort = myMgr->Ports(0);


	//Find, label, enable the node (node means motor)
	if (myPort.NodeCount() != 1) {
		/* ********************************************************************************************
			Pipe ERROR or just let it figure out C failed and closed
		********************************************************************************************** */
		return -1;
	}

	INode& theNode = myPort.Nodes(0);
	theNode.EnableReq(false);
	myMgr->Delay(200);
	theNode.Status.AlertsClear();
	theNode.Motion.NodeStopClear();
	theNode.EnableReq(true);

	double timeout = myMgr->TimeStampMsec() + TIME_TILL_TIMEOUT;
	while (!theNode.Motion.IsReady()) {
		if (myMgr->TimeStampMsec() > timeout) {
			return -2;
			/* ****************************************************************
				Pipe ERROR or just let it figure out C failed and closed
			******************************************************************/
		}
	}

	//C receive pipe
	HANDLE fromPy = CreateFile(
		L"\\\\.\\pipe\\Foo",
		GENERIC_READ | GENERIC_READ, // only need read access
		FILE_SHARE_READ | FILE_SHARE_WRITE,
		NULL,
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		NULL
	);

	if (fromPy == INVALID_HANDLE_VALUE) {
		printf("Failed to connect to python pipe.");
		// look up error code here using GetLastError()
		system("pause");
		return 1;
	}

	//C send pipe
	HANDLE toPy = CreateNamedPipe(
		L"\\\\.\\pipe\\Fan", // name of the pipe; python expects to read from Fan, so that is where we write
		PIPE_ACCESS_OUTBOUND, // 1-way pipe -- send only
		PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE, // send data as a byte stream or as a message
		1, // only allow 1 instance of this pipe
		0, // no outbound buffer
		0, // no inbound buffer
		0, // use default wait time
		NULL // use default security attributes
	);
		//make sure the pipe exists
	if (toPy == NULL || toPy == INVALID_HANDLE_VALUE) {
		printf("Failed to create outbound pipe.");
		// look up error code here using GetLastError()
		system("pause");
		return 1;
	}
		//wait for a connection from Python end
	BOOL connectedPipe = ConnectNamedPipe(toPy, NULL);
	if (!connectedPipe) {
		printf("Failed to make connection on named pipe.");
		// look up error code here using GetLastError()
		CloseHandle(toPy); // close the pipe
		system("pause");
		//return 1;
	}

	while (1) {

		/* *****************************************************************************************************
			Recieve pipe value
			Store as pipeCom
		******************************************************************************************************** */
		// The read operation will block until there is data to read
		wchar_t buffer[128];	//original

		DWORD numBytesRead = 0;
		//this reads to buffer....
		BOOL sawFile = ReadFile(
			fromPy,
			buffer, // the data from the pipe will be put here
			127 * sizeof(wchar_t), // number of bytes allocated
			&numBytesRead, // this will store number of bytes actually read
			NULL // not using overlapped IO
		);

		int pipeCom = 0;

		//buffer needs to be processed and placed into pipeCom!
		//if data was read, process the data
		if (sawFile) {
			buffer[numBytesRead / sizeof(wchar_t)] = '\0'; // null terminate the string

			//get the numeric ascii value of the data received
			pipeCom = (int)buffer[0];

			////we must convert the wchar_t array buffer to a char* array
			//size_t origsize = wcslen(buffer) + 1;
			//const size_t newsize = 100;
			//size_t convertedChars = 0;
			//char nstring[newsize];
			//wcstombs_s(&convertedChars, nstring, origsize, buffer, _TRUNCATE);
			////convert that new string nstring to long int!!!!!
			//char* garbage = NULL;
			//pipeCom = strtol(nstring, &garbage, 0);
		

		}
		else {
			printf("Failed to read data from the pipe.");
		}
		//now the data is processed
		//receive int pipeCyom from python every loop!


		//Initialize and Home
		if (pipeCom == 1) {

			//Home motor
			if (theNode.Motion.Homing.HomingValid()) {
				theNode.Motion.Homing.Initiate();

				timeout = myMgr->TimeStampMsec() + TIME_TILL_TIMEOUT;
				while (!theNode.Motion.Homing.WasHomed()) {
					if (myMgr->TimeStampMsec() > timeout) {
						return -2;
					}
				}
			}
			else {

			}
		

			pipeCom = 0;
		}


		//Torque Feedback
		else if (pipeCom == 2) {
			theNode.TrqUnit(theNode.PCT_MAX);
			theNode.Motion.TrqMeasured.Refresh();
			theTrq = double(theNode.Motion.TrqMeasured);
			wchar_t word[17];
			swprintf_s(word, 17, L"%f", theTrq);
			sendData(toPy, connectedPipe, word);

		}


		//Fire motor
		else if (pipeCom > 5) {

			int speed = 0;

			//Move Motor Up
			switch (pipeCom) {
				case 6:
					speed = 65;
					break;
				case 7:
					speed = 70;
					break;
				case 8:
					speed = 75;
					break;
				case 9:
					speed = 80;
					break;
				case 10:
					speed = 85;
					break;

				case 11:
					speed = 90;
					break;

				case 12:
					speed = 110;
					break;

				case 13:
					speed = 125;
					break;

				case 14:
					speed = 150;
					break;

				case 15:
					speed = 165;
					break;

				case 16:
					speed = 200;
					break;

				case 17:
					speed = 270;
					break;

				case 18:
					speed = 310;
					break;

				case 19:
					speed = 610;
					break;

				case 20:
					speed = 680;
					break;

				case 21:
					speed = 950;
					break;

				case 22:
					speed = 1440;
					break;

				case 23:
					speed = 1700;
					break;

				case 24:
					speed = 2080;
					break;

				case 25:
					speed = 2130;
					break;

				default:
					speed = 2130;
			}


			theNode.Motion.MoveWentDone();
			theNode.AccUnit(INode::RPM_PER_SEC);
			theNode.VelUnit(INode::RPM);
			theNode.Motion.AccLimit = ACC_LIM_RPM_PER_SEC;
			theNode.Motion.VelLimit = speed;


			auto time = std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
			theNode.Motion.MovePosnStart(MOVE_DISTANCE_CNTS);

			double speed1 = myMgr->TimeStampMsec();

			double timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 1000;
			while (!theNode.Motion.MoveIsDone()) {
				theNode.Motion.VelMeasured.Refresh();
				//printf("%lg\n", double(theNode.Motion.VelMeasured));
				if (double(theNode.Motion.VelMeasured) < 0) {
					break;
				}
				if (myMgr->TimeStampMsec() > timeout) {
					printf("Never finished");

					return -2;
				}
			}

			double speed2 = myMgr->TimeStampMsec();
			//printf("Duration: %lg\n", (speed2 - speed1));

			double duration = speed2 - speed1;

			printf("Time of fire: %lld\n", time);
			//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			// send the time here
			wchar_t word[21];
			swprintf_s(word, 21, L"%lld", time);
			sendData(toPy, connectedPipe, word);
			
			long long dur = ceil(duration);

			//Move motor back to home

			myMgr->Delay(1500);
			theNode.Motion.MoveWentDone();
			theNode.Motion.VelLimit = 30;
			theNode.Motion.MovePosnStart(-MOVE_DISTANCE_CNTS);
			//send the duration...
			wchar_t otherWord[21];
			swprintf_s(otherWord, 21, L"%f", duration);
			sendData(toPy, connectedPipe, otherWord);

			timeout = myMgr->TimeStampMsec() + theNode.Motion.MovePosnDurationMsec(MOVE_DISTANCE_CNTS) + 1000;
			while (!theNode.Motion.MoveIsDone()) {
				if (myMgr->TimeStampMsec() > timeout) {
					return -2;
				}
			}
		}


		//Disable motor
		else if (pipeCom == 4) {
			myPort.Nodes(0).EnableReq(false);
			myMgr->PortsClose();

			//Close C program
			return 0;
		}
	}
}

