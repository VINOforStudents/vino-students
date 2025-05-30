from langchain_experimental.text_splitter import SemanticChunker
import chromadb.utils.embedding_functions as embedding_functions
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

# google_ef = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key) # Add this line
# text_splitter = SemanticChunker(google_ef,
#                                 breakpoint_threshold_type="percentile",
#                                 breakpoint_threshold_amount = 80,
#                                 min_chunk_size=200)
text = """SCRUM Methodology
===================

# Summary

Scrum is an agile framework for developing, delivering, and sustaining complex products, with an initial emphasis on software development, although it has been used in other fields. It is designed for teams of ten or fewer members, who break their work into goals that can be completed within time-boxed iterations, called sprints, typically two weeks to one month long. The Scrum Team tracks progress in 15-minute daily stand-up meetings, called Daily Scrums. At the end of the sprint, a Sprint Review is held to demonstrate the work done, and a Sprint Retrospective is conducted to continuously improve processes. Scrum is based on empiricism, meaning knowledge comes from experience and making decisions based on what is observed.

# Full Description

Scrum is a lightweight yet powerful framework that helps teams and organizations generate value through adaptive solutions for complex problems. It is not a definitive methodology but rather a framework within which various processes and techniques can be employed. Scrum emphasizes teamwork, accountability, and iterative progress toward a well-defined goal.

## Core principles

The framework is built upon three core pillars:

- **Transparency**: Significant aspects of the process must be visible to those responsible for the outcome. Transparency requires those aspects to be defined by a common standard so observers share a common understanding of what is being seen. For example, a common language referring to the process must be shared by all participants, and those performing the work and those inspecting the resulting increment must share a common definition of "Done."
  
- **Inspection**: Scrum artifacts and progress toward agreed goals must be inspected frequently and diligently to detect potentially undesirable variances or problems. To help with inspection, Scrum provides cadence in the form of its five events.
  
- **Adaptation**: If an inspector determines that one or more aspects of a process deviate outside acceptable limits, and that the resulting product will be unacceptable, the process or the material being processed must be adjusted. The adjustment must be made as soon as possible to minimize further deviation. Adaptation becomes more difficult when the people involved are not empowered or self-managing.

Scrum defines three **roles**, five **events**, and three **artifacts**.

## Roles

**Scrum roles**:

- **Product Owner (PO)**: Responsible for maximizing the value of the product resulting from the work of the Scrum Team. The PO manages the Product Backlog, which includes clearly expressing Product Backlog items, ordering them to best achieve goals and missions, and ensuring the Product Backlog is visible, transparent, and clear to all.
  
- **Scrum Master (SM)**: Responsible for promoting and supporting Scrum as defined in the Scrum Guide. Scrum Masters do this by helping everyone understand Scrum theory, practices, rules, and values. The SM is a servant-leader for the Scrum Team, helping to remove impediments to the team's progress.
  
- **Development Team (Developers)**: Professionals who do the work of delivering a potentially releasable Increment of "Done" product at the end of each Sprint. Developers are structured and empowered by the organization to organize and manage their own work.

## Events

**Scrum Events (all are time-boxed)**:

- **The Sprint**: The heart of Scrum, a time-box of one month or less during which a "Done," usable, and potentially releasable product Increment is created. Sprints have consistent durations throughout a development effort. A new Sprint starts immediately after the conclusion of the previous Sprint.
  
- **Sprint Planning**: Work to be performed in the Sprint is planned. This plan is created by the collaborative work of the entire Scrum Team. It answers: What can be delivered in the Increment resulting from the upcoming Sprint? How will the work needed to deliver the Increment be achieved?
  
- **Daily Scrum**: A 15-minute meeting for the Developers of the Scrum Team to synchronize activities and create a plan for the next 24 hours. This is done by inspecting the work since the last Daily Scrum and forecasting upcoming Sprint work.
  
- **Sprint Review**: Held at the end of the Sprint to inspect the Increment and adapt the Product Backlog if needed. The Scrum Team presents the results of their work to key stakeholders and progress toward the Product Goal is discussed.
  
- **Sprint Retrospective**: An opportunity for the Scrum Team to inspect itself and create a plan for improvements to be enacted during the next Sprint. It occurs after the Sprint Review and prior to the next Sprint Planning.
  
## Artifacts

Scrum Artifacts:

- **Product Backlog**: An emergent, ordered list of what is needed to improve the product. It is the single source of work undertaken by the Scrum Team. The Product Owner is responsible for its content, availability, and ordering.
  
- **Sprint Backlog**: The set of Product Backlog items selected for the Sprint, plus a plan for delivering the product Increment and realizing the Sprint Goal. The Sprint Backlog is a forecast by the Developers about what functionality will be in the next Increment and the work needed to deliver that functionality into a "Done" Increment.
  
- **Increment**: The sum of all the Product Backlog items completed during a Sprint and the value of the increments of all previous Sprints. At the end of a Sprint, the new Increment must be "Done," which means it is in a usable condition and meets the Scrum Team’s definition of "Done."

# Application Area

While Scrum was initially developed for software development projects, its principles and structure are adaptable to a wide variety of complex work. It is particularly effective in situations where:

- Requirements are complex and likely to change: Scrum's iterative nature allows for flexibility and adaptation as the project progresses and understanding deepens.
- Speed-to-market is a critical factor: Sprints deliver functional increments quickly, allowing for early feedback and value delivery.
- Innovation and creativity are desired: Scrum empowers teams and encourages collaborative problem-solving.
- Cross-functional teamwork is essential: Scrum roles and events foster close collaboration between different skill sets.
- 
## Application Examples

Examples of application areas beyond software include:
- Research and development
- Marketing campaigns
- Product management
- Organizational change initiatives
- Education (e.g., project-based learning)
- Event planning
For ICT students, Scrum is highly relevant for group projects, capstone projects, and understanding modern development practices prevalent in the industry.

# Step-by-Step Guide (Simplified Project Lifecycle)

This is a simplified view of how a project might flow using Scrum:

1.	**Vision & Product Backlog Creation**:
- The Product Owner, with input from stakeholders, defines the product vision and creates an initial
- Product Backlog – a prioritized list of features, requirements, enhancements, and fixes.
- Actionable for students: For a group project, define your project goal and list all the features you want to build. Prioritize them.
  
2.	**Sprint Planning**:
- The Scrum Team (Product Owner, Scrum Master, Developers) meets.
- The Product Owner presents the top-priority items from the Product Backlog.
- The Developers select how much work they can commit to completing in the upcoming Sprint (typically 2-4 weeks). This becomes the Sprint Backlog.
- The team defines a Sprint Goal – an objective for the Sprint.
- Actionable for students: As a team, decide which features from your project list you can realistically complete in the next 2 weeks. Define a clear goal for this period.
  
3.	**The Sprint (Execution)**:
- The Developers work on the items in the Sprint Backlog to create a potentially releasable product Increment.
- Daily Scrum: Each day, the Developers meet for 15 minutes to discuss:
    - What did I do yesterday that helped the Development Team meet the Sprint Goal?
    - What will I do today to help the Development Team meet the Sprint Goal?
    - Do I see any impediments that prevent me or the Development Team from meeting the Sprint Goal?

- The Scrum Master helps remove any identified impediments.
- The Product Owner is available to answer questions about the Product Backlog items.
- Actionable for students: Work on your selected tasks. Have a brief daily check-in to discuss progress, plans, and any roadblocks.
  
4.	**Sprint Review**:
- At the end of the Sprint, the Scrum Team and stakeholders (e.g., a professor, other students) review what was accomplished (the Increment).
- The Developers demonstrate the working product.
- The Product Owner discusses the Product Backlog and potential future work.
- Feedback is gathered.
- Actionable for students: Demonstrate what you've built to your coaches or peers. Get feedback.
  
5.	**Sprint Retrospective**:
- After the Sprint Review and before the next Sprint Planning.
- The Scrum Team reflects on the past Sprint: What went well? What could be improved? What will we commit to improve in the next Sprint?
- The goal is to identify actionable improvements to the team's process, tools, or collaboration.
- Actionable for students: Discuss as a team what worked well during the 2-week period, what didn't, and what you'll do differently next time.
  
6.	**Repeat**:
- The cycle (Sprint Planning, Sprint, Daily Scrums, Sprint Review, Sprint Retrospective) repeats until the product vision is achieved or the Product Owner decides to stop development. The Product Backlog evolves throughout the project.
  
# Considerations

- **Team Size**: Scrum is most effective with small, co-located (or well-connected virtually) teams, typically 3-9 Developers.
- **Commitment & Discipline**: Scrum requires commitment from all team members and discipline to follow the framework's events and principles.
- **Definition of "Done"**: A clear, shared understanding of what "Done" means for an Increment is crucial for transparency and quality. This should be established early.
- **Self-Organization**: Developers are expected to self-organize to determine how best to accomplish their work. This requires trust and empowerment.
- Scrum Master Role: The Scrum Master is not a project manager in the traditional sense. They are a facilitator, coach, and impediment remover.
- **Product Owner Availability**: The Product Owner must be available to the team to clarify requirements and make decisions about the Product Backlog.
- **Adaptability**: Be prepared to adapt the process. Scrum is a framework, not a rigid methodology. The Sprint Retrospective is key for this.
- **Learning Curve**: While simple to understand, Scrum can be challenging to master. It often requires a shift in mindset.
- **Tooling**: Various tools can support Scrum (e.g., Jira, Trello, Asana), but they are secondary to understanding and implementing the principles. Simple physical boards can be very effective.
  
# Resource Links

- **The Scrum Guide**: The definitive guide to Scrum, co-authored by Ken Schwaber and Jeff Sutherland. This is the primary source for understanding Scrum.
  - URL: https://scrumguides.org
- **Scrum.org**: Offers resources, assessments, and certifications for Scrum.
  - URL: https://www.scrum.org
- **Scrum Alliance**: Another organization offering resources, certifications, and community for Scrum practitioners.
  - URL: https://www.scrumalliance.org
"""

# docs = text_splitter.create_documents([text], metadatas=[{"source": "example_text"}])

# for i, doc in enumerate(docs):
#     print(f"Chunk {i+1}: {doc.page_content} \n ============ END OF CHUNK ============ \n")

import pypandoc

# output = pypandoc.convert_file('kb_new/SCRUM.md', 'plain', format='md', extra_args = ["--toc", "--standalone"])
# print(output)

import re

def identify_doc_type(doc):
    '''
    categorizes a plaintext doc based on the format of the toc.
    '''
    # Look for TOC pattern: lines starting with "- " followed by double newline and then content
    if re.search(r'- .*\r?\n\r?\n[A-Z]', doc):
        return "TOC_WITHOUT_TITLE"
    else:
        return "NO_TOC_TITLE"

def read_doc(path):
    '''
    reads a text file and returns toc and full text.
    '''
    doc = str(pypandoc.convert_file(path, 'plain', format='md', extra_args = ["--toc", "--standalone"]))
    doc_type = identify_doc_type(doc)

    if doc_type == "TOC_WITH_TITLE":
        doc = re.sub('.*\n\n\n-', '-', doc)
        toc, text = doc.split('\n\n', 1)
    elif doc_type == "TOC_WITHOUT_TITLE":
        # Split on double newline/carriage return to separate TOC from content
        parts = re.split(r'\r?\n\r?\n', doc, 1)
        if len(parts) >= 2:
            toc, text = parts[0], parts[1]
        else:
            toc, text = "", doc
    else:
        toc, text = "", doc

    return toc, text

def cleanup_plaintext(text):
    '''
    gets the full text of a document and returns cleaned-up text.
    '''
    # Remove images
    text = text.replace("[image]", "")
    text = text.replace("[]", "")

    # First normalize line endings - convert \r\n to \n
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')

    # Replace single \n with space EXCEPT when:
    # - followed by another \n (paragraph break)
    # - followed by "- " (bullet point)
    # - preceded by a bullet point and followed by "- " (between bullet points)
    text = re.sub('(?<!\n)\n(?!(\n|- ))', ' ', text)

    # Replace any sequence of two or more newlines with \n\n
    text = re.sub('\n{2,}', '\n\n', text)

    # Replace multiple spaces with single space
    text = re.sub('(?<!\n) +', ' ', text)
    return text

def split_text(toc, text):
    '''
    gets the toc and cleaned text, and returns chunks of texts:
    ["Heading [SEP] Text", ]
    '''
    # Handle empty TOC case
    if not toc.strip():
        headings = []
    else:
        # Split TOC by newlines and extract headings, handling carriage returns
        toc_lines = re.split(r'\r?\n', toc)
        headings = []
        for line in toc_lines:
            # Strip bullets and whitespace, handle indented items
            cleaned_line = line.strip('- \n\r').strip()
            if cleaned_line:
                headings.append(cleaned_line)
    
    paragraphs = text.split("\n\n")

    current_heading = ""
    current_content = []
    text_chunks = []
    
    for para in paragraphs:
        # Skip empty paragraphs
        if not para.strip():
            continue

        # Check if this paragraph is a heading
        if len(headings) > 0 and para.strip() in headings:
            # Save the previous heading and its content as a chunk
            if current_heading and current_content:
                combined_content = " ".join(current_content)
                text_chunks.append(f"{current_heading} [SEP] {combined_content}".strip())
            
            # Start new heading
            current_heading = para.strip()
            headings.remove(para.strip())
            current_content = []
            continue

        # Accumulate content under the current heading
        current_content.append(para.strip())

    # Don't forget to add the last heading and its content
    if current_heading and current_content:
        combined_content = " ".join(current_content)
        text_chunks.append(f"{current_heading} [SEP] {combined_content}".strip())
    elif current_content and not current_heading:
        # Handle content without headings
        combined_content = " ".join(current_content)
        text_chunks.append(combined_content.strip())

    return text_chunks

import pandas as pd

df = pd.DataFrame()
root_dir = 'kb_new'
allowed_filetypes = ['.md', '.docx', '.pdf']

print(f"Walking directory: {os.path.abspath(root_dir)}") # Check if the path is correct

for directory, subdirectories, files in os.walk(root_dir):
    print(f"In directory: {directory}") # Check which directory is being processed
    for file in files:
        filename, filetype = os.path.splitext(file)
        if filetype in allowed_filetypes:
            full_path = os.path.join(directory, file)
            print(f"Processing file: {full_path}") # Check if files are being found

            toc, text = read_doc(full_path)
            print(f"  TOC length: {len(toc)}, Text length: {len(text)}") # Check output of read_doc

            text_cleaned = cleanup_plaintext(text)
            print(f"  Cleaned text length: {len(text_cleaned)}") # Check output of cleanup_plaintext

            text_chunks = split_text(toc, text_cleaned)
            print(f"  Number of chunks: {len(text_chunks)}") # Crucial check: is text_chunks empty?
            if not text_chunks:
                print(f"    No chunks generated for {full_path}")
            for chunk in text_chunks:
                print(f"==========    Chunk: \n{chunk}\n==========") # Check output of split_text
            df_new = pd.DataFrame(text_chunks, columns=["text"])
            df_new[["directory", "filename", "filetype"]] = directory, filename, filetype
            df = pd.concat([df, df_new])
        # else: # Optional: print files that are skipped
        #     print(f"Skipping file (wrong type): {os.path.join(directory, file)}")


df.reset_index(drop=True, inplace=True)
print(df.head(100))