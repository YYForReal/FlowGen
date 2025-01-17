# PowerShell script to setup Draw.io files
$sourceDir = "../../drawio/src/main/webapp"
$targetDir = "../public/drawio"

# Create target directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $targetDir

# Copy required directories
$dirs = @(
    "js",
    "styles",
    "images",
    "resources"
)

foreach ($dir in $dirs) {
    Write-Host "Copying $dir..."
    Copy-Item -Path "$sourceDir/$dir" -Destination "$targetDir/$dir" -Recurse -Force
}

# Copy index.html
Write-Host "Copying index.html..."
Copy-Item -Path "$sourceDir/index.html" -Destination "$targetDir/index.html" -Force

Write-Host "Setup complete!" 