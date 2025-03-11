# GitHub Repository Setup Instructions

This document outlines the steps to set up two GitHub repositories:
1. A personal repository for the generalized CompExtractor tool
2. A TPZ-specific fork for the ZoneSight adaptation

## 1. Setting Up the Personal CompExtractor Repository

### 1.1. Create a New GitHub Repository

1. Log in to GitHub with your personal account (fizt656)
2. Create a new repository named "compextractor"
3. Make it public
4. Do not initialize with README, .gitignore, or license (we'll push these from local)

### 1.2. Prepare the Local Repository

1. Create a new directory for the CompExtractor version:
   ```bash
   mkdir -p ~/Documents/repos/compextractor-personal
   ```

2. Copy the generalized files to the new directory:
   ```bash
   cp -r src ~/Documents/repos/compextractor-personal/
   cp requirements.txt ~/Documents/repos/compextractor-personal/
   cp .env.example ~/Documents/repos/compextractor-personal/
   cp tpz-specific/README_GENERAL.md ~/Documents/repos/compextractor-personal/README.md
   cp tpz-specific/LICENSE_GENERAL ~/Documents/repos/compextractor-personal/LICENSE
   cp .gitignore ~/Documents/repos/compextractor-personal/
   cp Compextractor_Banner_Gus.png ~/Documents/repos/compextractor-personal/banner.jpeg
   cp sound.mp3 ~/Documents/repos/compextractor-personal/
   cp coin.mp3 ~/Documents/repos/compextractor-personal/
   ```

3. Initialize the Git repository and push to GitHub:
   ```bash
   cd ~/Documents/repos/compextractor-personal
   git init
   git add .
   git commit -m "Initial commit of CompExtractor"
   git branch -M main
   git remote add origin https://github.com/fizt656/compextractor.git
   git push -u origin main
   ```

## 2. Setting Up the TPZ-Specific ZoneSight Repository

### 2.1. Create a New GitHub Organization

1. Log in to GitHub with the TPZ account (TPZgus)
2. Create a new organization named "ThePossibleZone"
3. Choose the free plan

### 2.2. Fork the CompExtractor Repository

1. Navigate to https://github.com/fizt656/compextractor
2. Click the "Fork" button
3. Select the "ThePossibleZone" organization as the owner
4. Name the repository "zonesight"
5. Click "Create fork"

### 2.3. Customize the TPZ Fork

1. Clone the forked repository:
   ```bash
   git clone https://github.com/ThePossibleZone/zonesight.git ~/Documents/repos/zonesight
   cd ~/Documents/repos/zonesight
   ```

2. Replace the README.md with the TPZ-specific version:
   ```bash
   cp ~/Documents/repos/compextractor\ 2/README.md ~/Documents/repos/zonesight/
   ```

3. Replace the LICENSE with the TPZ-specific version:
   ```bash
   cp ~/Documents/repos/compextractor\ 2/LICENSE ~/Documents/repos/zonesight/
   ```

4. Replace the banner image:
   ```bash
   cp ~/Documents/repos/compextractor\ 2/ZoneSight_banner_tpz.png ~/Documents/repos/zonesight/banner.jpeg
   ```

5. Copy the TPZ-specific files:
   ```bash
   cp ~/Documents/repos/compextractor\ 2/In\ the\ Zone.mp3 ~/Documents/repos/zonesight/
   ```

6. Commit and push the changes:
   ```bash
   git add .
   git commit -m "Customize for TPZ-specific use"
   git push
   ```

## 3. Maintaining the Repositories

### 3.1. Pulling Updates from CompExtractor to ZoneSight

When you make improvements to the CompExtractor repository that should also be applied to ZoneSight:

1. Add the upstream repository (only needed once):
   ```bash
   cd ~/Documents/repos/zonesight
   git remote add upstream https://github.com/fizt656/compextractor.git
   ```

2. Pull changes from upstream:
   ```bash
   git fetch upstream
   git merge upstream/main
   # Resolve any conflicts
   git push
   ```

### 3.2. Making TPZ-Specific Changes

When making changes specific to the TPZ version:

1. Make the changes directly in the ZoneSight repository
2. Commit and push to the TPZ repository:
   ```bash
   git add .
   git commit -m "Add TPZ-specific feature"
   git push
   ```

## 4. Running the Applications

### 4.1. Running CompExtractor

```bash
cd ~/Documents/repos/compextractor-personal
python src/compextractor_gui.py
```

### 4.2. Running ZoneSight

```bash
cd ~/Documents/repos/zonesight
python src/zonesight_gui.py
```
