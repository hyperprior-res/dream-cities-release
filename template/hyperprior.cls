\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{hyperprior}[2026/10/17 HyperPrior Research working papers]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[11pt,a4paper,twocolumn]{article}
\RequirePackage[british]{babel}
\RequirePackage{amsmath,amsthm}
\RequirePackage[T1]{fontenc}
\RequirePackage[type1]{XCharter}
\RequirePackage[xcharter,bigdelims,vvarbb]{newtxmath}
\RequirePackage[scaled=1.1]{zlmtt}
\renewcommand{\encodingdefault}{T1}
\fontencoding{T1}\selectfont
\RequirePackage{microtype}
\RequirePackage[left=22mm,right=22mm,top=30mm,bottom=30mm,headheight=40pt,headsep=20pt]{geometry}
\RequirePackage{xcolor,graphicx,booktabs,tabularx,multirow}
\RequirePackage{fancyhdr,titlesec,caption,enumitem}
\RequirePackage[authoryear,round,sort&compress]{natbib}
\RequirePackage{hyperref}
\definecolor{hprred}{HTML}{8E1B1E}
\definecolor{hprblue}{HTML}{0072B2}
\definecolor{hprrule}{gray}{0.5}
\hypersetup{colorlinks=true,allcolors=hprblue,pdfcreator={HyperPrior Research},pdfauthor={icebreaker, rangivz, e1}}
\raggedbottom
% Permit final-width empirical panels beside their discussion instead of
% deferring an entire double-column float queue until after the references.
\renewcommand{\dbltopfraction}{0.9}
\setlength{\columnsep}{15pt}
\setlength{\parskip}{0.5\baselineskip}
\setlist[itemize]{noitemsep}
\setlist[enumerate]{noitemsep}
\setcounter{secnumdepth}{3}
\newcommand{\hprtitle}{}
\newcommand{\hprauthors}{icebreaker, rangivz and e1}
\newcommand{\hpraffiliation}{HyperPrior Research, London}
\newcommand{\hprabstract}{}
\newcommand{\hprkeywords}{}
\newcommand{\hprdate}{\number\year-\ifnum\month<10 0\fi\number\month-\ifnum\day<10 0\fi\number\day}
\newcommand{\hprwordmark}{wordmark.pdf}
\newif\ifhprworkingpaper
\newcommand{\hprversion}{}
\newcommand{\hprpriorconfidence}{}
\newcommand{\hprrevisitdate}{}
\NewDocumentCommand{\workingpaper}{mmm}{%
  \gdef\hprversion{#1}\gdef\hprpriorconfidence{#2}\gdef\hprrevisitdate{#3}%
  \global\hprworkingpapertrue}
\RenewDocumentCommand{\title}{m}{\gdef\hprtitle{#1}\hypersetup{pdftitle={#1}}}
\RenewDocumentCommand{\author}{m}{\gdef\hprauthors{#1}}
\RenewDocumentCommand{\date}{m}{\gdef\hprdate{#1}}
\NewDocumentCommand{\affiliation}{m}{\gdef\hpraffiliation{#1}}
\NewDocumentCommand{\keywords}{m}{\gdef\hprkeywords{#1}}
\NewDocumentCommand{\wordmarkpath}{m}{\gdef\hprwordmark{#1}}
\RenewDocumentEnvironment{abstract}{+b}{\gdef\hprabstract{#1}}{}
\newcommand{\hprsmall}{\normalfont\fontsize{8}{10}\selectfont}
\newcommand{\hprmetafont}{\normalfont\fontsize{7}{9}\selectfont\color{black!65}}
\newcommand{\hprmetasep}{\enspace\textbar\enspace}
\newcommand{\hprmetadata}{\ifhprworkingpaper
  {\hprmetafont Version \hprversion\hprmetasep\hprdate\hprmetasep
   Prior confidence \hprpriorconfidence\hprmetasep Revisit \hprrevisitdate}\fi}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\hprsmall\hprtitle}
\fancyfoot[L]{\hprmetadata}
\fancyfoot[R]{\hprsmall\thepage}
\renewcommand{\headrulewidth}{1pt}
\renewcommand{\footrulewidth}{1pt}
\renewcommand{\headrule}{\vskip0pt{\color{hprrule}\hrule height1pt width\headwidth}\vskip0pt}
\renewcommand{\footrule}{\vskip2.764pt{\color{hprrule}\hrule height1pt width\headwidth}\vskip1.236pt}
\fancypagestyle{hprfirst}{%
  \fancyhf{}
  \fancyhead[L]{\includegraphics[height=18pt]{\hprwordmark}}
  \fancyhead[R]{\hprsmall\itshape\hprdate\hspace*{6.1pt}}
  \fancyfoot[L]{\hprsmall\itshape Correspondence via \href{https://hyperprior.net}{hyperprior.net}\\\upshape\textcopyright\ 2026 HyperPrior Research}
  \fancyfoot[R]{\ifhprworkingpaper\parbox[t]{0.58\textwidth}{\raggedleft\hprmetafont
    Version \hprversion\hprmetasep\hprdate\\
    Prior confidence \hprpriorconfidence\hprmetasep Revisit \hprrevisitdate}\fi}
}
\RenewDocumentCommand{\maketitle}{}{%
  \twocolumn[\begin{minipage}{\textwidth}
  \setlength{\parindent}{0pt}
  \vspace*{2.73pt}
  {\raggedright\normalfont\bfseries\fontsize{21}{23}\selectfont\hprtitle\par}
  \vspace{11pt}
  {\raggedright\normalfont\bfseries\fontsize{9}{13}\selectfont\hprauthors\par}
  \vspace{0.7pt}
  {\raggedright\normalfont\fontsize{8}{10}\selectfont\hpraffiliation\par}
  \vspace{17.5pt}
  {\normalfont\bfseries\linespread{1.2}\fontsize{10}{12}\selectfont\hprabstract\par}
  \if\relax\detokenize\expandafter{\hprkeywords}\relax\else
    \vspace{1em}
    {\normalfont\itshape\linespread{1.2}\fontsize{11}{12}\selectfont Keywords: \hprkeywords\par}
  \fi
  \vspace{20pt}
  \end{minipage}]
  \thispagestyle{hprfirst}
}
\titleformat{\section}{\normalfont\bfseries\fontsize{13}{14}\selectfont}{\thesection.}{0.5em}{}
\titleformat{\subsection}{\normalfont\bfseries}{\thesubsection.}{0.5em}{}
\titleformat{\subsubsection}{\normalfont\bfseries\itshape}{\thesubsubsection.}{0.5em}{}
\titlespacing*{\section}{0pt}{3ex plus4pt minus3pt}{5pt}
\titlespacing*{\subsection}{0pt}{2.5ex plus3pt minus2pt}{2pt}
\titlespacing*{\subsubsection}{0pt}{2ex plus2.5pt minus1.5pt}{2pt}
\DeclareCaptionLabelSeparator{hprbar}{ $\vert$ }
\captionsetup{labelfont=normalfont,labelsep=hprbar,singlelinecheck=false,justification=justified}
\bibliographystyle{abbrvnat}
\endinput
