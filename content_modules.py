# content_modules.py

# This file stores curated, foundational content for popular learning paths.
# The content is used to provide a reliable starting point for explanations and quizzes.

CURATED_MODULES = {
    "SQL Fundamentals": {
        "description": "Learn the basics of Structured Query Language (SQL) to manage and query relational databases.",
        "content": """
        SQL (Structured Query Language) is the standard language for relational database management systems. 
        It is used to create, read, update, and delete data from databases. Key concepts include:
        - **Tables**: Data is stored in tables, which consist of rows and columns.
        - **Queries**: You use queries to ask questions of your database.
        - **SELECT Statement**: The most common command, used to retrieve data. The basic syntax is `SELECT column_name FROM table_name;`.
        - **WHERE Clause**: Used to filter records based on a specific condition. For example, `SELECT * FROM Users WHERE country = 'USA';`.
        - **JOINs**: Used to combine rows from two or more tables based on a related column between them. Common types are INNER JOIN, LEFT JOIN, and RIGHT JOIN.
        - **Primary Key**: A unique identifier for each record in a table.
        - **Foreign Key**: A key used to link two tables together.
        """
    },
    "Data Structures & Algorithms (DSA) Basics": {
        "description": "Understand the fundamental building blocks of efficient software.",
        "content": """
        Data Structures and Algorithms (DSA) are crucial for writing efficient and scalable code.
        - **Data Structures**: Ways of organizing and storing data. Common examples include:
          - **Arrays**: A collection of items stored at contiguous memory locations.
          - **Linked Lists**: A linear collection of data elements whose order is not given by their physical placement in memory.
          - **Stacks**: A Last-In, First-Out (LIFO) structure.
          - **Queues**: A First-In, First-Out (FIFO) structure.
          - **Trees**: A hierarchical structure with a root value and subtrees of children.
          - **Graphs**: A set of nodes (vertices) and edges that connect them.
        - **Algorithms**: A set of steps to accomplish a specific task. Key concepts include:
          - **Time Complexity**: How the runtime of an algorithm increases with the size of the input data (Big O notation).
          - **Space Complexity**: The amount of memory space required by an algorithm.
          - **Sorting Algorithms**: Such as Bubble Sort, Merge Sort, and Quick Sort.
          - **Searching Algorithms**: Such as Linear Search and Binary Search.
        """
    }
}