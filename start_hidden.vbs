' Bu skript telegram-bot-api serverini va Python botini
' HECH QANDAY OYNA KO'RSATMASDAN, orqa fonda ishga tushiradi.
' Kompyuter yoqiq bo'lsa yetarli — hech qanday oynani ochiq ushlab turish shart emas.

Set WshShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' 1. Local Telegram Bot API serverini yashirin ishga tushirish (agar mavjud bo'lsa)
apiServerPath = strPath & "\telegram-bot-api\telegram-bot-api.exe"
If CreateObject("Scripting.FileSystemObject").FileExists(apiServerPath) Then
    WshShell.Run """" & apiServerPath & """ --local --api-id=YOUR_API_ID --api-hash=YOUR_API_HASH", 0, False
    WScript.Sleep 3000 ' server ishga tushishini biroz kutamiz
End If

' 2. Telegram botini yashirin ishga tushirish
WshShell.CurrentDirectory = strPath
WshShell.Run "pythonw.exe bot.py", 0, False
