/* MacroHook.c — DLL inyectada en LU4 para enviar teclas sin foco
   Compilar: gcc -shared -o MacroHook.dll MacroHook.c -luser32 -lkernel32 -m64
*/
#include <windows.h>
#include <stdlib.h>
#include <string.h>

static DWORD WINAPI PipeThread(LPVOID p) {
    (void)p;
    for (;;) {
        /* Crear servidor de pipe — se reinicia en cada desconexión */
        HANDLE hPipe = CreateNamedPipeW(
            L"\\\\.\\pipe\\MacroLU4",
            PIPE_ACCESS_INBOUND,
            PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT,
            PIPE_UNLIMITED_INSTANCES, 0, 64, 0, NULL);

        if (hPipe == INVALID_HANDLE_VALUE) { Sleep(500); continue; }

        ConnectNamedPipe(hPipe, NULL);   /* espera al cliente Python */

        char buf[16];
        DWORD nr;
        while (ReadFile(hPipe, buf, sizeof(buf) - 1, &nr, NULL) && nr > 0) {
            buf[nr] = '\0';
            if (buf[0] != 'F') continue;
            int n = atoi(buf + 1);          /* "F1".."F12" */
            if (n < 1 || n > 12) continue;
            WORD vk = (WORD)(0x6F + n);     /* F1=0x70 .. F12=0x7B */

            INPUT dn, up;
            memset(&dn, 0, sizeof(INPUT));
            memset(&up, 0, sizeof(INPUT));
            dn.type = INPUT_KEYBOARD; dn.ki.wVk = vk;
            up.type = INPUT_KEYBOARD; up.ki.wVk = vk;
            up.ki.dwFlags = KEYEVENTF_KEYUP;

            SendInput(1, &dn, sizeof(INPUT));
            Sleep(50);
            SendInput(1, &up, sizeof(INPUT));
        }
        CloseHandle(hPipe);
    }
    return 0;
}

BOOL APIENTRY DllMain(HMODULE hMod, DWORD reason, LPVOID r) {
    (void)hMod; (void)r;
    if (reason == DLL_PROCESS_ATTACH)
        CreateThread(NULL, 0, PipeThread, NULL, 0, NULL);
    return TRUE;
}
