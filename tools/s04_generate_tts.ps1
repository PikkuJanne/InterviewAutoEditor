# Local development fixtures only. Never consumes interview media or transcripts.
param([Parameter(Mandatory=$true)][string]$Folder)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$s04Folder = (Resolve-Path -LiteralPath $Folder).Path
$s04Synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $s04Synth.SelectVoice('Microsoft David Desktop')
    $s04Cues = @{
        'synthetic-speech.wav' = 'This is a quiet development sample. Every spoken word should stay available.'
        'synthetic-yes.wav' = 'Yes.'
        'synthetic-mm.wav' = 'Mm hmm.'
    }
    foreach ($s04Name in $s04Cues.Keys) {
        $s04Target = Join-Path $s04Folder $s04Name
        if (Test-Path -LiteralPath $s04Target) { throw 'Synthetic destination already exists.' }
        $s04Synth.SetOutputToWaveFile($s04Target)
        $s04Synth.Speak($s04Cues[$s04Name])
        $s04Synth.SetOutputToNull()
    }
} finally { $s04Synth.Dispose() }
