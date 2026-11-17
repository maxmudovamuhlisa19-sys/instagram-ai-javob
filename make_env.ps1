$tok = (Get-Content 'C:\Users\sardor\Desktop\instagrammmm\token.json' -Raw | ConvertFrom-Json).access_token
$lines = @(
  'VERIFY_TOKEN=webhook_verify_2026',
  'PAGE_ACCESS_TOKEN=' + $tok,
  'IG_USER_ID=17841440771225406',
  'OPENAI_API_KEY=',
  'SYSTEM_PROMPT=Sen Jasurning Instagram hisobida avtomatik javob berasan. Qisqa, dostona va foydali javob ber. Javoblar o''zbek tilida yozilsin.'
)
[System.IO.File]::WriteAllLines('C:\Users\sardor\Desktop\instagrammmm\.env', $lines)
Write-Output ('env written, token len: ' + $tok.Length)
