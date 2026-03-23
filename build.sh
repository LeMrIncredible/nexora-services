#!/bin/bash

# This script orchestrates the integration of the Life OS application into the
# Nexora Services static site. It runs during the Netlify build step. The
# process is as follows:
# 1. Extract the Life OS archive (life-os-fixed.zip) into a working directory.
# 2. Patch the Next.js configuration to enable static export.
# 3. Install the Life OS dependencies via npm.
# 4. Build and export the Life OS application to a static output.
# 5. Copy the exported files into the public/lifeos directory to be
#    published alongside the existing site.
#
# It is safe to run this script multiple times; it removes any previous
# life_os work directory before extracting a fresh copy.

set -eo pipefail

echo "[Life OS] Starting integration build..."

# Define working directories
WORK_DIR="life_os_work"
EXPORT_DIR="public/lifeos"

# Clean any previous working directory
rm -rf "$WORK_DIR" "$EXPORT_DIR"

# Extract the Life OS archive into the working directory
echo "[Life OS] Extracting archive..."
unzip -q "life-os-fixed.zip" -d "$WORK_DIR"

# Navigate into the extracted Life OS project
cd "$WORK_DIR"

# Replace next.config.js with a custom configuration that enables static export
# and provides fallbacks for Node.js core modules that are not available
# in the browser environment. Without these fallbacks, Next.js will try
# to bundle modules like `fs` and `child_process`, which causes the
# build to fail on Netlify. We also preserve reactStrictMode for
# consistency with the original project.
echo "[Life OS] Writing next.config.js for static export and module fallbacks..."
cat > next.config.js <<'EOF_CFG'
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Export static HTML and assets so the site can be served from the public folder.
  output: 'export',
  webpack: (config) => {
    // Provide fallbacks for Node.js core modules that are not available in the browser.
    config.resolve.fallback = {
      ...(config.resolve.fallback || {}),
      fs: false,
      child_process: false,
    };
    return config;
  },
};

module.exports = nextConfig;
EOF_CFG

# Install dependencies. Netlify's build environment provides network
# access to npm, so this should succeed. Use --legacy-peer-deps to avoid
# peer dependency conflicts.
echo "[Life OS] Installing dependencies..."
npm install --legacy-peer-deps --no-audit --progress=false

# Install missing FontAwesome dependencies required by Life OS
# Put them in a separate install command to ensure they are available
# before building the application.
echo "[Life OS] Installing FontAwesome dependencies..."
npm install @fortawesome/react-fontawesome @fortawesome/free-solid-svg-icons @fortawesome/fontawesome-svg-core --legacy-peer-deps --no-audit --progress=false

# Work around an upstream bug in @fortawesome/react-fontawesome: it attempts
# to require a misspelled module path ("@fortawesom/fontawesome-svg-core")
# instead of the correct "@fortawesome/fontawesome-svg-core". Without
# intervention this causes a build failure on Netlify because the module
# cannot be resolved. To handle this, create a directory alias under
# node_modules/@fortawesom that symlinks back to the correct package. If
# the alias already exists, the commands below will silently succeed.
echo "[Life OS] Creating alias for '@fortawesom/fontawesome-svg-core'..."
mkdir -p node_modules/@fortawesom
if [ ! -e node_modules/@fortawesom/fontawesome-svg-core ]; then
  ln -s ../@fortawesome/fontawesome-svg-core node_modules/@fortawesom/fontawesome-svg-core || true
fi

# Build and export the Life OS application to a static site. The export
# command outputs to the default 'out' directory.
echo "[Life OS] Building application..."
npm run build

echo "[Life OS] Exporting static site..."
npx next export

# Create the export destination in the repository root and copy files
cd ..
mkdir -p "$EXPORT_DIR"
echo "[Life OS] Copying exported files to $EXPORT_DIR..."
cp -r "$WORK_DIR/out/"* "$EXPORT_DIR/"

echo "[Life OS] Integration complete."
