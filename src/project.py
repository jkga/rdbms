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

        # Check for SQL statement types
        if statement_context.select_statement():
            return self.handle_select(statement_context.select_statement()[0])
        if statement_context.insert_statement():
            return self.handle_insert(statement_context.insert_statement()[0])
        if statement_context.delete_statement():
            return self.handle_delete(statement_context.delete_statement()[0])

        return "No valid SQL statement found."

    def handle_select(self, select_statement_context):
        columns = self.extract_columns(select_statement_context.column_list())
        tables = [self.get_table_name(tc.getText()) for tc in select_statement_context.table_list()]
        conditions = self.extract_conditions(select_statement_context.where_clause()) if select_statement_context.where_clause() else None
        return self.execute_select_query(columns, tables, conditions)

    def handle_insert(self, insert_statement_context):
        table_name = self.get_table_name(insert_statement_context.table_list().WORD(0).getText())
        values = self.extract_values(insert_statement_context.values_list())
        return self.execute_insert_query(table_name, values)

    def handle_delete(self, delete_statement_context):
        table_name = self.get_table_name(delete_statement_context.table_list().WORD(0).getText())
        conditions = self.extract_conditions(delete_statement_context.where_clause()) if delete_statement_context.where_clause() else None
        return self.execute_delete_query(table_name, conditions)

    def extract_columns(self, column_list_context):
        columns = [col.getText() for col in column_list_context.getTypedRuleContexts(SQLParser.ColumnContext)]
        return [col.strip() for col in ','.join(columns).split(',')]

    def extract_values(self, values_list_context):
        values = []
        for value_context in values_list_context.value():
            if value_context.STRING():
                values.append(value_context.STRING().getText().strip("'"))
            elif value_context.NUMBER():
                values.append(int(value_context.NUMBER().getText()))
            else:
                values.append(value_context.getText())
        return values

    def extract_conditions(self, where_clause_context):
        conditions = []
        for expression in where_clause_context.condition_list().getTypedRuleContexts(SQLParser.ExpressionContext):
            conditions.append(expression.getText())
        return conditions

    def execute_select_query(self, columns, tables, conditions):
        table_name = tables[0] if tables else None
        csv_path = self.get_csv_path(table_name)
        if not os.path.exists(csv_path):
            return f"Error: Table '{table_name}' not found."

        try:
            with open(csv_path, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

                if conditions:
                    rows = [row for row in rows if all(self.evaluate_condition(row, cond) for cond in conditions)]

                if columns == ["*"] or not columns:
                    columns = reader.fieldnames
                else:
                    columns = [col for col in columns if col in reader.fieldnames]

                display_rows = [{col: row[col] for col in columns if col in row} for row in rows]
                return tabulate(display_rows, headers="keys", tablefmt="grid") if display_rows else "No records found."
        except Exception as e:
            return f"An error occurred while reading the CSV file: {e}"

    def execute_insert_query(self, table_name, values):
        csv_path = self.get_csv_path(table_name)
        try:
            with open(csv_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(values)
            return "Insert successful."
        except Exception as e:
            return f"An error occurred while writing to the CSV file: {e}"

    def execute_delete_query(self, table_name, conditions):
        csv_path = self.get_csv_path(table_name)
        if not os.path.exists(csv_path):
            return f"Error: Table '{table_name}' not found."

        try:
            with open(csv_path, mode='r') as file:
                reader = csv.DictReader(file)
                rows = list(reader)

            original_row_count = len(rows)

            if conditions:
                rows = [row for row in rows if not any(self.evaluate_condition(row, cond) for cond in conditions)]

            # Write back only if rows have changed
            if len(rows) < original_row_count:
                with open(csv_path, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                    writer.writeheader()
                    writer.writerows(rows)
                return "Delete successful."
            else:
                return "No rows matched the delete conditions."

        except Exception as e:
            return f"An error occurred while writing to the CSV file: {e}"

    def evaluate_condition(self, row, condition):
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1].strip()

        # Determine the operator and split the condition accordingly
        for operator in ['>=', '<=', '>', '<', '=', '!=']:
            if operator in condition:
                column, value = condition.split(operator)
                column = column.strip()
                value = value.strip().strip("'")
                break
        else:
            return False  # Invalid condition

        # Get the value from the row
        row_value = row.get(column)

        # Debug output
        print(f"Evaluating condition: {condition} | row_value: {row_value} | value: {value}")

        # Convert row_value for comparison
        try:
            if isinstance(row_value, str) and row_value.isdigit():
                row_value = int(row_value)
            else:
                row_value = float(row_value) if '.' in str(row_value) else int(row_value)

            # Convert value for comparison
            value = float(value) if '.' in value else int(value)
        except ValueError:
            # If there's a conversion issue, treat values as strings
            row_value = str(row_value)
            value = str(value)

        # Compare based on the operator
        if operator == '=':
            return row_value == value
        elif operator == '>':
            return row_value > value
        elif operator == '<':
            return row_value < value
        elif operator == '>=':
            return row_value >= value
        elif operator == '<=':
            return row_value <= value
        elif operator == '!=':
            return row_value != value

        return False

    def get_table_name(self, table_name):
        mapping = {
            'course': 'course_table',
            'courseoffering': 'courseoffering_table',
            'studcourse': 'studcourse_table',
            'student': 'student_table',
            'studenthistory': 'studenthistory_table',
        }
        return mapping.get(table_name.lower(), table_name)

    def get_csv_path(self, table_name):
        table_map = {
            "course_table": "data/course_table.csv",
            "student_table": "data/student_table.csv",
            "courseoffering_table": "data/courseoffering_table.csv",
            "studcourse_table": "data/studcourse_table.csv",
            "studenthistory_table": "data/studenthistory_table.csv",
        }
        return table_map.get(table_name, None)

class RDBMS_GUI:
    def __init__(self, root, sql_handler):
        self.sql_handler = sql_handler
        root.title("RDBMS GUI")
        root.geometry("1500x530")
        root.configure(bg='white')

        tk.Label(root, text="Enter SQL Query:", bg='white', fg='black').pack(pady=5)
        input_frame = tk.Frame(root, bg='white')
        input_frame.pack(pady=5)

        self.query_entry = tk.Text(input_frame, height=2, width=170, bg='white', fg='black')
        self.query_entry.pack(side=tk.LEFT)

        self.execute_button = tk.Button(input_frame, text="Execute Query", command=self.execute_query, bg='black', fg='white', height=2)
        self.execute_button.pack(side=tk.LEFT, padx=5)

        tk.Label(root, text="Output:", bg='white', fg='black').pack(pady=5)
        self.output_area = scrolledtext.ScrolledText(root, height=25, width=184, state='disabled', bg='black', fg='green')
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
            self.output_area.insert(tk.END, result)

        except Exception as e:
            self.output_area.insert(tk.END, f"An error occurred while processing the query: {e}")
        finally:
            self.output_area.config(state='disabled')
            self.query_entry.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    sql_handler = SQLHandler()
    rdbms_gui = RDBMS_GUI(root, sql_handler)
    root.mainloop()
