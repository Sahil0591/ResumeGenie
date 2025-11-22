\documentclass[11pt]{article}
\usepackage[letterpaper, top=0.5in, bottom=0.5in, left=0.5in, right=0.5in]{geometry}

\usepackage[utf8]{inputenc}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{titlesec}
\raggedright
\pagestyle{empty}
\input{glyphtounicode}
\pdfgentounicode=1

\titleformat{\section}{\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule\vspace{-6.5pt}]
\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$}
\setlist[itemize]{itemsep=-2pt, leftmargin=12pt, topsep=7pt}

\begin{document}

\begin{center}
\Huge Jane Doe
\end{center}

\vspace{5pt}

\href{mailto:jane.doe@gmail.com}{jane.doe@gmail.com} | \href{https://github.com/jane-doe}{github.com/jane-doe} | \href{https://www.linkedin.com/in/jane-doe}{linkedin.com/in/jane-doe}

\vspace{-10pt}

\section*{Skills}
\textbf{Programming Languages:} Python, JavaScript, TypeScript \\
\textbf{Frameworks:} React, Node.js, Express \\
\textbf{Cloud Platforms:} AWS, Google Cloud Platform \\
\textbf{DevOps:} Terraform, Docker, Kubernetes \\
\textbf{Databases:} SQL, MongoDB \\
\textbf{Version Control:} Git

\vspace{-6.5pt}

\section*{Achievements}
\textbf{Led migration to AWS with Infrastructure as Code:} Moved legacy services to AWS using Terraform, reducing infrastructure costs by 30\%.
\begin{itemize}
    \item Action: Migrated legacy services to AWS
    \item Context: Implemented Infrastructure as Code with Terraform
    \item Result: Reduced infrastructure costs by 30\%
\end{itemize}

\textbf{Developed real-time data processing pipeline:} Built a scalable data processing pipeline using Python, Kafka, and AWS Kinesis, enabling real-time analytics for a client.
\begin{itemize}
    \item Action: Developed real-time data processing pipeline
    \item Context: Utilized Python, Kafka, and AWS Kinesis
    \item Result: Enabled real-time analytics for the client
\end{itemize}


\end{document}
