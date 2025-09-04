#include <windows.h>
#include <iostream>
#include <string>

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Usage: process_clone_ext.exe <original_pid> <father_pid> <count>\n";
        return 1;
    }

    DWORD original_pid = std::stoi(argv[1]);
    DWORD father_pid   = std::stoi(argv[2]);
    int count          = std::stoi(argv[3]);

    // Получаем путь exe оригинального процесса
    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, original_pid);
    if (!hProc) {
        std::cerr << "Cannot open original process\n";
        return 1;
    }

    char exePath[MAX_PATH];
    DWORD size = MAX_PATH;
    if (!QueryFullProcessImageNameA(hProc, 0, exePath, &size)) {
        std::cerr << "Cannot get executable path\n";
        CloseHandle(hProc);
        return 1;
    }
    CloseHandle(hProc);

    // Для каждого клона
    for (int i = 0; i < count; i++) {
        STARTUPINFOEXA si;
        ZeroMemory(&si, sizeof(si));
        si.StartupInfo.cb = sizeof(STARTUPINFOEXA);

        // Создаём атрибут-лист для указания Parent PID
        SIZE_T attrSize = 0;
        InitializeProcThreadAttributeList(NULL, 1, 0, &attrSize);
        si.lpAttributeList = (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(GetProcessHeap(), 0, attrSize);
        InitializeProcThreadAttributeList(si.lpAttributeList, 1, 0, &attrSize);

        HANDLE parentHandle = OpenProcess(PROCESS_CREATE_PROCESS, FALSE, father_pid);
        if (!parentHandle) {
            std::cerr << "Cannot open father process\n";
            DeleteProcThreadAttributeList(si.lpAttributeList);
            HeapFree(GetProcessHeap(), 0, si.lpAttributeList);
            continue;
        }

        UpdateProcThreadAttribute(
            si.lpAttributeList,
            0,
            PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,
            &parentHandle,
            sizeof(HANDLE),
            NULL,
            NULL
        );

        PROCESS_INFORMATION pi;
        BOOL result = CreateProcessA(
            exePath,
            NULL,
            NULL,
            NULL,
            FALSE,
            EXTENDED_STARTUPINFO_PRESENT | CREATE_SUSPENDED,
            NULL,
            NULL,
            &si.StartupInfo,
            &pi
        );

        if (result) {
            std::cout << pi.dwProcessId << std::endl;
            CloseHandle(pi.hThread);
            CloseHandle(pi.hProcess);
        } else {
            std::cerr << "Failed to create clone\n";
        }

        CloseHandle(parentHandle);
        DeleteProcThreadAttributeList(si.lpAttributeList);
        HeapFree(GetProcessHeap(), 0, si.lpAttributeList);
    }

    return 0;
}
