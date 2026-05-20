# Creates a portable ZIP archive of this project.
# Run from anywhere: the project root is detected from this script location.
[CmdletBinding()]
param(
    # Optional output path. By default, the archive is created next to the project folder.
    [string]$OutputPath,

    # Use this switch if you do not want the top-level project folder inside the ZIP.
    [switch]$NoRootFolder
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$projectRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$projectName = Split-Path -Path $projectRoot -Leaf
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'

if ([string]::IsNullOrWhiteSpace($OutputPath)) {
    # Keep the ZIP outside the project by default so it is not archived into itself.
    $OutputPath = Join-Path -Path (Split-Path -Path $projectRoot -Parent) -ChildPath "$projectName`_$timestamp.zip"
}

$archivePath = [System.IO.Path]::GetFullPath($OutputPath)
$rootPrefix = if ($NoRootFolder) { '' } else { "$projectName/" }

function Convert-ToRelativePath {
    param(
        [Parameter(Mandatory = $true)][string]$BasePath,
        [Parameter(Mandatory = $true)][string]$TargetPath
    )

    # Windows PowerShell 5.1 has no [System.IO.Path]::GetRelativePath, so use Uri.
    $base = [System.IO.Path]::GetFullPath($BasePath).TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    $target = [System.IO.Path]::GetFullPath($TargetPath)
    $baseUri = [Uri]$base
    $targetUri = [Uri]$target

    return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace('/', [System.IO.Path]::DirectorySeparatorChar)
}

function Test-IsExcludedDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $normalized = $RelativePath.Replace('/', '\').TrimStart('\')

    # Skip large dependency/runtime directories before recursion.
    if (
        $normalized -ieq 'Backend\.venv' -or
        $normalized -ieq 'Backend\.vent' -or
        $normalized -ieq 'Backend\.pytest_cache' -or
        $normalized -ieq 'Frontend\node_modules'
    ) {
        return $true
    }

    return $false
}

function Test-IsExcludedFile {
    param(
        [Parameter(Mandatory = $true)][System.IO.FileInfo]$File,
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    $normalized = $RelativePath.Replace('/', '\').TrimStart('\')

    # Exclude direct files in docs whose names start with open, sun, or Hanwha.
    if ($normalized -match '^(?i:docs)\\[^\\]+$') {
        $fileName = [System.IO.Path]::GetFileName($normalized)
        if ($fileName -match '^(?i:open|sun|Hanwha)') {
            return $true
        }
    }

    # If the output path is inside the project, do not add it to the archive.
    $itemPath = [System.IO.Path]::GetFullPath($File.FullName)
    if ([string]::Equals($itemPath, $archivePath, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }

    return $false
}

function Add-ZipEntryForDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath
    )

    if ([string]::IsNullOrWhiteSpace($RelativePath)) {
        return
    }

    $entryName = $rootPrefix + $RelativePath.Replace('\', '/') + '/'
    [void]$zip.CreateEntry($entryName)
    $script:directoryCount++
}

function Add-ProjectDirectory {
    param(
        [Parameter(Mandatory = $true)][System.IO.DirectoryInfo]$Directory
    )

    $relative = Convert-ToRelativePath -BasePath $projectRoot -TargetPath $Directory.FullName
    Add-ZipEntryForDirectory -RelativePath $relative

    foreach ($childDirectory in Get-ChildItem -LiteralPath $Directory.FullName -Directory -Force) {
        $childRelative = Convert-ToRelativePath -BasePath $projectRoot -TargetPath $childDirectory.FullName

        if (Test-IsExcludedDirectory -RelativePath $childRelative) {
            Write-Host "Skip directory: $childRelative"
            continue
        }

        Add-ProjectDirectory -Directory $childDirectory
    }

    foreach ($file in Get-ChildItem -LiteralPath $Directory.FullName -File -Force) {
        $fileRelative = Convert-ToRelativePath -BasePath $projectRoot -TargetPath $file.FullName

        if (Test-IsExcludedFile -File $file -RelativePath $fileRelative) {
            $script:skippedFileCount++
            continue
        }

        $entryName = $rootPrefix + $fileRelative.Replace('\', '/')
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
            $zip,
            $file.FullName,
            $entryName,
            [System.IO.Compression.CompressionLevel]::Optimal
        ) | Out-Null

        $script:fileCount++
        if (($script:fileCount % 100) -eq 0) {
            Write-Host "Added files: $script:fileCount"
        }
    }
}

if (Test-Path -LiteralPath $archivePath) {
    Remove-Item -LiteralPath $archivePath -Force
}

$archiveDirectory = Split-Path -Path $archivePath -Parent
if (-not [string]::IsNullOrWhiteSpace($archiveDirectory) -and -not (Test-Path -LiteralPath $archiveDirectory)) {
    New-Item -ItemType Directory -Path $archiveDirectory -Force | Out-Null
}

$fileCount = 0
$directoryCount = 0
$skippedFileCount = 0

Write-Host "Project root: $projectRoot"
Write-Host "Archive path: $archivePath"
Write-Host "Excluded: docs\open*, docs\sun*, docs\Hanwha*, Backend\.venv, Backend\.vent, Backend\.pytest_cache, Frontend\node_modules"

$zip = [System.IO.Compression.ZipFile]::Open($archivePath, [System.IO.Compression.ZipArchiveMode]::Create)

try {
    # Walk the tree manually so excluded directories are pruned before recursion.
    Add-ProjectDirectory -Directory (Get-Item -LiteralPath $projectRoot)
}
finally {
    $zip.Dispose()
}

$archiveSizeMb = [Math]::Round((Get-Item -LiteralPath $archivePath).Length / 1MB, 2)
Write-Host "Archive created: $archivePath"
Write-Host "Size: $archiveSizeMb MB"
Write-Host "Directories added: $directoryCount"
Write-Host "Files added: $fileCount"
Write-Host "Files skipped by rules: $skippedFileCount"
