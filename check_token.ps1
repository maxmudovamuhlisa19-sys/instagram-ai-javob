$j = Get-Content 'C:\Users\sardor\Desktop\instagrammmm\token.json' -Raw | ConvertFrom-Json
$props = $j.PSObject.Properties.Name
Write-Output ('fields: ' + ($props -join ','))
if ($j.access_token) { Write-Output ('token_len: ' + $j.access_token.Length) }
if ($j.expires_in) { Write-Output ('expires_in: ' + $j.expires_in) }
if ($j.error) { Write-Output ('error: ' + ($j.error | ConvertTo-Json -Compress)) }
