import tkinter as tk
from tkinter import messagebox, scrolledtext
from antlr4 import *
from compiler.parser.SQLParser import SQLParser
from compiler.parser.SQLLexer import SQLLexer
from tabulate import tabulate
import os
import csv


class SQLHandler:
    def handle_sql_statement(self, statement):
        statement_context = statement[0] if isinstance(statement, list) else statement

        # Check for SELECT statement
        select_statements = statement_context.select_statement()
        if select_statements:
            return self.handle_select(select_statements[0])

        # Check for INSERT statement
        insert_statements = statement_context.insert_statement()
        if insert_statements:
            return self.handle_insert(insert_statements[0])

        # Check for DELETE statement
        delete_statements = statement_context.delete_statement()
        if delete_statements:
            return self.handle_delete(delete_statements[0])

        return "No valid SQL statement found."  # Output for invalid statements

    def handle_select(self, select_statement_context):
        column_list_context = select_statement_context.column_list()
        columns = self.extract_columns(column_list_context)

        tables = []
        table_list_contexts = select_statement_context.table_list()
        for table_context in table_list_contexts:
            table_name = table_context.getText()
            tables.append(table_name)

        where_clause_context = select_statement_context.where_clause()
        conditions = self.extract_conditions(where_clause_context) if where_clause_context else None
        return self.execute_select_query(columns, tables, conditions)

    def handle_insert(self, insert_statement_context):
        table_list_context = insert_statement_context.table_list()
        if table_list_context is None:
            return "No table specified in INSERT statement."

        if hasattr(table_list_context, 'WORD'):
            table_name = table_list_context.WORD(0).getText()
        else:
            return "Table list context does not have WORD attribute."

        values_context = insert_statement_context.values_list()
        if values_context is None:
            return "No values specified in INSERT statement."

        values = self.extract_values(values_context)
        return self.execute_insert_query(table_name, values)

    def handle_delete(self, delete_statement_context):
        table_list_context = delete_statement_context.table_list()
        if table_list_context is None:
            return "No table specified in DELETE statement."

        table_name = table_list_context.WORD(0).getText()
        where_clause_context = delete_statement_context.where_clause()
        conditions = self.extract_conditions(where_clause_context) if where_clause_context else None
        return self.execute_delete_query(table_name, conditions)

    def extract_columns(self, column_list_context):
        # Split columns by comma in case they're not parsed correctly
        columns = [column.getText() for column in column_list_context.getTypedRuleContexts(SQLParser.ColumnContext)]
        # Handle any combined columns (like "CNo, CTitle")
        split_columns = []
        for col in columns:
            split_columns.extend(col.split(','))  # Split on comma and add each part to split_columns
        return [col.strip() for col in split_columns]  # Strip whitespace from column names

    def extract_values(self, values_list_context):
        values = []
        if values_list_context is None:
            return values

        for value_context in values_list_context.value():
            if value_context is None:
                continue
            if hasattr(value_context, 'STRING') and value_context.STRING() is not None:
                values.append(value_context.STRING().getText().strip("'"))
            elif hasattr(value_context, 'NUMBER') and value_context.NUMBER() is not None:
                values.append(int(value_context.NUMBER().getText()))
            else:
                values.append(value_context.getText())
        return values

    def extract_conditions(self, where_clause_context):
        conditions = []
        condition_list_context = where_clause_context.condition_list()
        for expression in condition_list_context.getTypedRuleContexts(SQLParser.ExpressionContext):
            conditions.append(expression.getText())
        return conditions

    def execute_select_query(self, columns, tables, conditions):
        if not tables:
            return "Error: No table specified in SELECT statement."

        table_name = tables[0]
        table_map = {
            "course_table": "data/course_table.csv",
            "student_table": "data/student_table.csv",
            "courseoffering_table": "data/courseoffering_table.csv",
            "studcourse_table": "data/studcourse_table.csv",
            "studenthistory_table": "data/studenthistory_table.csv",
        }

        if table_name in table_map:
            csv_path = table_map[table_name]
            if not os.path.exists(csv_path):
                return f"Error: Table '{table_name}' not found."

            try:
                with open(csv_path, mode='r') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                    # Filter rows based on conditions, if any
                    if conditions:
                        rows = [row for row in rows if all(self.evaluate_condition(row, cond) for cond in conditions)]

                    # Ensure columns are limited to existing fields in the CSV
                    if columns == ["*"] or not columns:
                        columns = reader.fieldnames
                    else:
                        columns = [col for col in columns if col in reader.fieldnames]

                    # Always include NoOfUnits in the output
                    if "NoOfUnits" not in columns:
                        columns.append("NoOfUnits")

                    # Prepare display_rows to include all necessary data
                    display_rows = [
                        {col: row[col] for col in columns if col in row} for row in rows
                    ]

                    # Check if any rows matched the conditions
                    if not display_rows:
                        return "No records found."

                    # Return tabulated output
                    return tabulate(display_rows, headers="keys", tablefmt="grid")
            except Exception as e:
                return f"An error occurred while reading the CSV file: {e}"
        else:
            return f"Error: Table '{table_name}' not found."

    def execute_insert_query(self, table_name, values):
        table_map = {
            "course_table": "data/course_table.csv",
            "student_table": "data/student_table.csv",
            "courseoffering_table": "data/courseoffering_table.csv",
            "studcourse_table": "data/studcourse_table.csv",
            "studenthistory_table": "data/studenthistory_table.csv",
        }

        if table_name in table_map:
            csv_path = table_map[table_name]
            try:
                # Append the new values to the CSV file
                with open(csv_path, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(values)
                return "Insert successful."
            except Exception as e:
                return f"An error occurred while writing to the CSV file: {e}"
        return f"Error: Table '{table_name}' not found."

    def execute_delete_query(self, table_name, conditions):
        table_map = {
            "course_table": "data/course_table.csv",
            "student_table": "data/student_table.csv",
            "courseoffering_table": "data/courseoffering_table.csv",
            "studcourse_table": "data/studcourse_table.csv",
            "studenthistory_table": "data/studenthistory_table.csv",
        }

        if table_name in table_map:
            csv_path = table_map[table_name]
            if not os.path.exists(csv_path):
                return f"Error: Table '{table_name}' not found."

            try:
                with open(csv_path, mode='r') as file:
                    reader = csv.DictReader(file)
                    rows = list(reader)

                if conditions is None or len(conditions) == 0:
                    rows.clear()
                    with open(csv_path, mode='w', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=rows[0].keys() if rows else [])
                        writer.writeheader()
                        writer.writerows(rows)
                    return "All rows deleted from the table."
                else:
                    rows = [row for row in rows if not all(self.evaluate_condition(row, cond) for cond in conditions)]

                with open(csv_path, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=rows[0].keys() if rows else [])
                    writer.writeheader()
                    writer.writerows(rows)

                return "Delete successful."
            except Exception as e:
                return f"An error occurred while writing to the CSV file: {e}"

    def evaluate_condition(self, row, condition):
        column, value = condition.split('=')
        column = column.strip()
        value = value.strip().strip("'")

        if value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit():
            value = float(value)

        row_value = row.get(column)
        if row_value is None:
            return False

        return str(row_value) == str(value)


class RDBMS_GUI:
    def __init__(self, root, sql_handler):
        self.sql_handler = sql_handler

        root.title("RDBMS GUI")
        root.geometry("1500x530")
        root.configure(bg='white')  # Set background color to white

        tk.Label(root, text="Enter SQL Query:", bg='white', fg='black').pack(pady=5)

        # Create a frame to hold the Text and Button side by side
        input_frame = tk.Frame(root, bg='white')
        input_frame.pack(pady=5)

        self.query_entry = tk.Text(input_frame, height=2, width=170, bg='white', fg='black')  # Increase width from 100 to 120
        self.query_entry.pack(side=tk.LEFT)

        self.execute_button = tk.Button(input_frame, text="Execute Query", command=self.execute_query, bg='black', fg='white', height=2)  # Black button, white text
        self.execute_button.pack(side=tk.LEFT, padx=5)  # Add some padding between the button and the text area

        tk.Label(root, text="Output:", bg='white', fg='black').pack(pady=5)
        self.output_area = scrolledtext.ScrolledText(root, height=25, width=184, state='disabled', bg='black', fg='green')  # Black background, green text
        self.output_area.pack(pady=5)

        self.query_entry.bind("<Return>", lambda event: self.execute_query())

    def execute_query(self):
        query = self.query_entry.get("1.0", tk.END).strip()

        if not query:
            messagebox.showerror("Error", "Please enter an SQL query.")
            return

        self.output_area.config(state='normal')
        self.output_area.delete("1.0", tk.END)

        try:
            input_stream = InputStream(query)
            lexer = SQLLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = SQLParser(token_stream)
            tree = parser.sql_statement()

            result = self.sql_handler.handle_sql_statement(tree)
            self.output_area.insert(tk.END, result)  # Display result in the output area

        except Exception as e:
            self.output_area.insert(tk.END, f"An error occurred while processing the query: {e}")
        finally:
            self.output_area.config(state='disabled')

            # Clear the input box after executing the query
            self.query_entry.delete("1.0", tk.END)  # Clear the input box


if __name__ == "__main__":
    root = tk.Tk()
    sql_handler = SQLHandler()
    rdbms_gui = RDBMS_GUI(root, sql_handler)
    root.mainloop()
