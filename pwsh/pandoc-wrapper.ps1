#
# This example was taken from Microsoft's PowerShell-Docs Github repository
# (https://github.com/PowerShell/PowerShell-Docs), which demonstrates the
# download and usage of Pandoc to transform Markdown files into HTML, in a CI
# build.
 
param(
    [switch]$SkipCabs,
    [switch]$ShowProgress
)
 
# Turning off the progress display, by default
$global:ProgressPreference = 'SilentlyContinue'
if($ShowProgress){$ProgressPreference = 'Continue'}
 

# $pandocExePath = Join-Path (Join-Path $pandocDestinationPath "pandoc-$panDocVersion") "pandoc.exe"
$pandocExecPath = "figure this out after calling github-release-install.ps1"

## DOWNLOAD AND INSTALL LATEST CONFLUENCE LUA: https://github.com/jpbarrette/pandoc-confluence-writer/blob/master/confluence.lua
 
# Find the reference folder path w.r.t the script
$ReferenceDocset = Join-Path $PSScriptRoot 'reference'
 
# Variable to collect any errors in during processing
$allErrors = @()

## SHOULD THIS RECURSE

# Go through all the directories in the reference folder
Get-ChildItem $ReferenceDocset -Directory -Exclude 'docs-conceptual','mapping', 'bread-pscore' | ForEach-Object -Process {
    $Version = $_.Name
    $VersionFolder = $_.FullName
    # For each of the directories, go through each module folder
    Get-ChildItem $VersionFolder -Directory | ForEach-Object -Process {
        $ModuleName = $_
        $ModulePath = Join-Path $VersionFolder $_
 
        $LandingPage = Join-Path $ModulePath "$ModuleName.md"
        $MamlOutputFolder = Join-Path "$PSScriptRoot\maml" "$Version\$ModuleName"
        $CabOutputFolder = Join-Path "$PSScriptRoot\updatablehelp" "$Version\$ModuleName"
 
        if(-not (Test-Path $MamlOutputFolder))
        {
            New-Item $MamlOutputFolder -ItemType Directory -Force > $null
        }
 
        # Process the about topics if any
        $AboutFolder = Join-Path $ModulePath "About"
 
        if(Test-Path $AboutFolder)
        {
            Get-ChildItem "$aboutfolder/about_*.md" | ForEach-Object {
                $aboutFileFullName = $_.FullName
                $aboutFileOutputName = "$($_.BaseName).help.txt"
                $aboutFileOutputFullName = Join-Path $MamlOutputFolder $aboutFileOutputName
 
                $pandocArgs = @(
                    "--from=markdown",
                    "--to=plain+multiline_tables+inline_code_attributes",
                    "--columns=75",
                    "--output=$aboutFileOutputFullName",
                    $aboutFileFullName,
                    "--quiet"
                )
 
                & $pandocExePath $pandocArgs
            }
        }
 
        try {
            # For each module, create a single maml help file
            # Adding warningaction=stop to throw errors for all warnings, erroraction=stop to make them terminating errors
            New-ExternalHelp -Path $ModulePath -OutputPath $MamlOutputFolder -Force -WarningAction Stop -ErrorAction Stop
 
            # For each module, create update-help help files (cab and helpinfo.xml files)
            if (-not $SkipCabs) {
                $cabInfo = New-ExternalHelpCab -CabFilesFolder $MamlOutputFolder -LandingPagePath $LandingPage -OutputFolder $CabOutputFolder
 
                # Only output the cab fileinfo object
                if($cabInfo.Count -eq 8){$cabInfo[-1].FullName}
            }
        } catch {
            $allErrors += $_
        }
    }
}
 
# If the above block, produced any errors, throw and fail the job
if ($allErrors) {
    $allErrors
    throw "There are errors during platyPS run!`nPlease fix your markdown to comply with the schema: https://github.com/PowerShell/platyPS/blob/master/platyPS.schema.md"
}