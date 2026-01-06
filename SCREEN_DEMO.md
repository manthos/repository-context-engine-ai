# R2CE Screenshots and Video Demo

## Video Demo

🎥 **Watch the full demonstration**: [R2CE Demo Video](screenshots/R2CE-demo2.mp4)

This video shows the complete workflow of analyzing a repository, browsing the generated summaries, and querying the system. Github cannot show it, it has to be downloaded to view.

---

## Screenshots

### 1. Frontend Interface - Repository Analysis
![Frontend Main Interface](screenshots/Screenshot%20from%202026-01-06%2012-43-16.png)

The main interface showing the repository URL input, passphrase authentication, and analysis depth configuration.

---

### 2. Folder Recursive Analysis
![Folder Analysis](screenshots/Screenshot%20from%202026-01-06%2012-43-27.png)

Folder analysis from recursively analyzed contents.

---

### 3. File Analysis
![Repository Tree View & File Analysis](screenshots/Screenshot%20from%202026-01-06%2012-43-35.png)

Hierarchical tree visualization of the analyzed repository structure with expandable folders and file summaries.

---

### 4. Another folder Summary Details
![Folder Summary Details](screenshots/Screenshot%20from%202026-01-06%2012-43-45.png)

Detailed AI-generated summary for complete folders showing key contents, purpose, and dependencies.

---

### 5. Search Interface
![Search Interface](screenshots/Screenshot%20from%202026-01-06%2012-43-57.png)

Semantic search results showing relevant files and summaries based on query terms with highlighted matches.

---

### 6. Ask AI Results
![Ask AI Results](screenshots/Screenshot%20from%202026-01-06%2012-44-40.png)

Question-answering interface allowing natural language queries about the repository with context-aware responses.

---

## Features Demonstrated

✅ **Repository Analysis**: Input any public GitHub repository URL and analyze its structure  
✅ **Real-time Progress**: Live progress tracking with percentage completion and status messages  
✅ **Tree Navigation**: Browse repository structure with AI-generated summaries at every level  
✅ **Semantic Search**: Find relevant code and documentation using natural language queries  
✅ **Q&A System**: Ask questions about the repository and get AI-powered answers with sources  
✅ **Responsive UI**: Clean, modern interface with intuitive navigation and controls  

---

## How to Use

1. **Visit**: https://r2ce-frontend.onrender.com
2. **Enter Repository URL**: Any public GitHub repository
3. **Provide Passphrase**: Contact the author for evaluator access
4. **Start Analysis**: Click "Analyze" and watch the progress
5. **Explore Results**: Browse tree, search, or ask questions
6. **Persistent Storage**: All results saved to PostgreSQL and filesystem for future access

> ⚠️ **Note**: For Render deployment please note we are using free tier which means:
- **Cold starts**: Services spin down after 15 minutes of inactivity and take ~30 seconds to wake up
- **Ephemeral filesystem**: Cloned Git repositories (`backend/cache/`) are deleted on every deployment or spin-down
- Previously analyzed repositories will be wiped out from Render's filesystem 
this is not an R2CE issue but how free tier Render works
- **Please be patient** when first accessing - the service needs to boot up

