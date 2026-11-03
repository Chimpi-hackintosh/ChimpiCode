Unicode true
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!ifndef VERSION
  !define VERSION "1.1.0"
!endif
!ifndef RELEASE_DIR
  !error "Pass /DRELEASE_DIR with the absolute directory containing both MSI files"
!endif
Name "ChimpiCode ${VERSION}"
OutFile "${RELEASE_DIR}\ChimpiCode-${VERSION}-x64-Setup.exe"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
ShowInstDetails nevershow
VIProductVersion "${VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "ChimpiCode"
VIAddVersionKey /LANG=1033 "CompanyName" "SnoopyOS Company"
VIAddVersionKey /LANG=1033 "FileDescription" "ChimpiCode Windows installer"
VIAddVersionKey /LANG=1033 "FileVersion" "${VERSION}"
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "PortugueseBR"
LangString InstallError ${LANG_ENGLISH} "Installation failed. Windows Installer code: $0"
LangString InstallError ${LANG_PORTUGUESEBR} "Falha na instalação. Código do Windows Installer: $0"
LangString Need64 ${LANG_ENGLISH} "ChimpiCode requires 64-bit Windows."
LangString Need64 ${LANG_PORTUGUESEBR} "O ChimpiCode exige Windows de 64 bits."

Function .onInit
  System::Call 'kernel32::GetUserDefaultUILanguage() i .r1'
  IntOp $1 $1 & 0x3FF
  StrCpy $LANGUAGE ${LANG_ENGLISH}
  ${If} $1 == 22
    StrCpy $LANGUAGE ${LANG_PORTUGUESEBR}
  ${EndIf}
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "$(Need64)"
    SetErrorLevel 1633
    Quit
  ${EndIf}
FunctionEnd

Section
  InitPluginsDir
  SetOutPath "$PLUGINSDIR"
  ${If} $LANGUAGE == ${LANG_PORTUGUESEBR}
    File /oname=ChimpiCode.msi "${RELEASE_DIR}\ChimpiCode-${VERSION}-x64-pt-BR.msi"
  ${Else}
    File /oname=ChimpiCode.msi "${RELEASE_DIR}\ChimpiCode-${VERSION}-x64.msi"
  ${EndIf}
  ClearErrors
  IfSilent silent_install
  ExecWait '"$SYSDIR\msiexec.exe" /i "$PLUGINSDIR\ChimpiCode.msi" /norestart' $0
  Goto finished_install
  silent_install:
  ExecWait '"$SYSDIR\msiexec.exe" /i "$PLUGINSDIR\ChimpiCode.msi" /qn /norestart' $0
  finished_install:
  ${If} ${Errors}
    StrCpy $0 1603
  ${EndIf}
  ${If} $0 != 0
  ${AndIf} $0 != 3010
  ${AndIf} $0 != 1602
    IfSilent +2
    MessageBox MB_ICONSTOP "$(InstallError)"
  ${EndIf}
  SetErrorLevel $0
SectionEnd
