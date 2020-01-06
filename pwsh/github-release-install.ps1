# Download latest release from github

$repo = "jgm/pandoc"
$package = "pandoc"

$platform = "linux-amd64.tar.gz"

$platformFile = ""
$extension = "zip"
switch ($platform)
{
    "linux" { $platformFile = "linux-amd64"; $extension = "tar.gz" }
    "macOS" { $platformFile = "macOS" }
    "windows" { $platformFile = "windows-x86_64" }
}

$releases = "https://api.github.com/repos/$repo/releases"

Write-Host "Determining latest release"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$tag = (Invoke-WebRequest -Uri $releases -UseBasicParsing | ConvertFrom-Json)[0].tag_name

$file = "$package-$tag-$platformFile.$extension"
$dir = "$package-$tag-$platformFile"

$download = "https://github.com/$repo/releases/download/$tag/$file"

Write-Host "Downloading latest release"

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest $download -Out $zip

Write-Host "Extracting release files"
Expand-Archive $zip -Force

# Cleaning up target dir
Remove-Item $name -Recurse -Force -ErrorAction SilentlyContinue 

# Moving from temp dir to target dir
Move-Item "$dir\$name" -Destination $name -Force

# Removing temp files
Remove-Item $file -Force
Remove-Item $dir -Recurse -Force