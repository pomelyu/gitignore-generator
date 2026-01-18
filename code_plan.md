This repo is a cross-platform cmd tool that generates .gitignore file by asking users their requirements. To make this tool cross-platform and ready-to-use, it requires minimum third-party library.

Here are the requirements. Note that the requirements are not strict and please give me advise if there are better solutions and also help me to refine all the displayed texts in this tools.
1. implemented by python with minimum third-party library
2. use pyinstaller to package this project and automatically build and release in github
3. gitignore templates come from "https://github.com/github/gitignore". You can either clone it or use http request to browse the content. I'm not sure which way is better. Please read the following text about the folder structure in git templates
```
Folder structure

We support a collection of templates, organized in this way:

- The root folder contains templates in common use, to help people get started with popular programming languages and technologies. These define a meaningful set of rules to help get started, and ensure you are not committing unimportant files into your repository.
- **Global** contains templates for various editors, tools and operating systems that can be used in different situations. It is recommended that you either add these to your global template or merge these rules into your project-specific templates if you want to use them permanently.
- **community** contains specialized templates for other popular languages, tools and project, which don't currently belong in the mainstream templates. These should be added to your project-specific templates when you decide to adopt the framework or tool.
```

To better implement this repo with source control, please follow my step-by-step instruction.

### Step1.
Create an interatcive cmd tools like.
```bash
# If .gitignore is already existed, ask user
> Detect existing .gitignore. Do you want to overwrite it[y/n]? n
# If user choose "n" absort

# Choices are seperated by "," and case-insenstivie
# Some templates https://github.com/github/gitignore are under `Global` or `community` folder
# In this case, the name of template should include the path. For example, community/Python/JupyterNotebooks
# In this step, assume the input choices are all available. We will deal with the missing choice issue in the next step. However you have to reserve a function for the next step. Current the function is used to map "windows", "macOS", "Linux" to "Global/windows", "Global/Linux, "Global/macOS".
> Choose the operation system[windows,macOS,Linux]? windows,macOS,Linux
> Choose your programming language[python]? python
> Add other templates?

# Confirm the choice
> The following templates will be used
> OS: windows,macOS,Linux
> Language: python
> Others: xxx,xxx
> comfirm[y/n]?
```
The generated .gitignore looks like: use title to seperate different templates and merge them into a single file. Make sure to add `##### This Repo #####` in the end of the file to let use futher add their project specific files.
```
##### Windows #####
...
...
##### macOS #####
...
...
##### Python #####
...
##### This Repo #####

```
### Step2.
Refine the tool to search and deal with missing templates. For example the template I used is `myTemplate`
1. if there is only one file for `myTemplate`, I don't have to use full path, like `community/myTemplate`
2. if there are multiple files, list the choices and ask user to choose one.
3. if `myTemplate` is not available, list the candidates that has the same prefix, for example `community/myTemplate1`, `myTemplate2`

### Step3.
add pyinstaller and github CI/CD process
