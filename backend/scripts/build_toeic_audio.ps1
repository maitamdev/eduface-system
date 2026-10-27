# Windows-only authoring utility. Prebuilt WAV files are shipped for all platforms.
param([switch]$Force)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$taskRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$audioDir = Join-Path $taskRoot 'frontend/public/toeic/audio'
[System.IO.Directory]::CreateDirectory($audioDir) | Out-Null
$course = Get-Content -LiteralPath (Join-Path $taskRoot 'backend/data/toeic/course.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$available = @($synth.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name })
$primaryVoice = @('Microsoft David Desktop','Microsoft Hazel Desktop','Microsoft Zira Desktop') | Where-Object { $available -contains $_ } | Select-Object -First 1
if (-not $primaryVoice) { throw 'An English System.Speech voice is required to rebuild audio.' }
$femaleVoice = @('Microsoft Zira Desktop','Microsoft Hazel Desktop') | Where-Object { $available -contains $_ } | Select-Object -First 1
if (-not $femaleVoice) { $femaleVoice = $primaryVoice }
$format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(16000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
$manifest = @()
$prior = @{}
$manifestPath = Join-Path $audioDir 'manifest.json'
if (Test-Path -LiteralPath $manifestPath) {
  foreach ($row in (Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json)) { $prior[$row.id] = $row }
}
try {
  foreach ($question in ($course.questions | Where-Object { $_.audio_id } | Sort-Object audio_id -Unique)) {
    $audioPath = Join-Path $audioDir ($question.audio_id + '.wav')
    $hasher = [System.Security.Cryptography.SHA256]::Create()
    try { $transcriptHash = [System.BitConverter]::ToString($hasher.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($question.transcript))).Replace('-', '').ToLowerInvariant() } finally { $hasher.Dispose() }
    if (-not $Force -and $prior.ContainsKey($question.audio_id) -and (Test-Path -LiteralPath $audioPath) -and $prior[$question.audio_id].transcript_sha256 -eq $transcriptHash -and $prior[$question.audio_id].bytes -eq (Get-Item -LiteralPath $audioPath).Length) {
      $manifest += $prior[$question.audio_id]
      continue
    }
    $synth.SetOutputToWaveFile($audioPath, $format)
    $synth.Rate = -1
    foreach ($line in ($question.transcript -split "`n")) {
      if ($line.StartsWith('Woman:')) { $synth.SelectVoice($femaleVoice); $spoken = $line.Substring(6).Trim() }
      elseif ($line.StartsWith('Man:')) { $synth.SelectVoice($primaryVoice); $spoken = $line.Substring(4).Trim() }
      else { $synth.SelectVoice($primaryVoice); $spoken = $line }
      $synth.Speak($spoken)
    }
    $synth.SetOutputToNull()
    $manifest += @{id=$question.audio_id; file=($question.audio_id + '.wav'); bytes=(Get-Item -LiteralPath $audioPath).Length; synthetic=$true; sample_rate=16000; transcript_sha256=$transcriptHash; voices=@($primaryVoice,$femaleVoice)}
  }
} finally { $synth.Dispose() }
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $audioDir 'manifest.json') -Encoding UTF8
Write-Output ('Generated ' + $manifest.Count + ' local synthetic audio files.')
