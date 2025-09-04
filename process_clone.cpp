#include <windows.h>
#include <iostream>

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Usage: process_clone.exe <original_pid> <count>\n";
        return 1;
    }

    DWORD original_pid = std::stoi(argv[1]);
    int count = std::stoi(argv[2]);

    // Получаем путь исполняемого файла оригинального процесса
    HANDLE hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, original_pid);
    if (!hProc) {
        std::cerr << "Cannot open original process.\n";
        return 1;
    }

    char exePath[MAX_PATH];
    DWORD size = MAX_PATH;
    if (!QueryFullProcessImageNameA(hProc, 0, exePath, &size)) {
        std::cerr << "Cannot get executable path.\n";
        CloseHandle(hProc);
        return 1;
    }
    CloseHandle(hProc);

    for (int i = 0; i < count; i++) {
        STARTUPINFOA si = { sizeof(si) };
        PROCESS_INFORMATION pi;

        BOOL result = CreateProcessA(
            exePath,
            NULL,
            NULL,
            NULL,
            FALSE,
            CREATE_SUSPENDED,  // процесс заморожен
            NULL,
            NULL,
            &si,
            &pi
        );

        if (result) {
            std::cout << pi.dwProcessId << std::endl;
            CloseHandle(pi.hThread);
            CloseHandle(pi.hProcess);
        } else {
            std::cerr << "Failed to create clone.\n";
        }
    }

    return 0;
}
