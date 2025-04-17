import pdfplumber
import csv

class Conversion:
    
    def pdf_to_csv(self,pdf_path,csv_path):
        with pdfplumber.open(pdf_path) as pdf, open(csv_path, mode='w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            for page_num, page in enumerate(pdf.pages, start=1):
                tables = page.extract_tables()
                if tables:
                    csv_writer.writerow([f"Page {page_num}"])  # Write page number as header
                    for table in tables:
                        for row in table:
                            # Filter out empty cells and clean up rows
                            cleaned_row = [cell.replace('\n', ' ') if cell else '' for cell in row]
                            csv_writer.writerow(cleaned_row)
                        csv_writer.writerow([])  
                    statement=f"Processed tables on page {page_num}"
                    return statement
                else:
                    statement=f"No tables found on page {page_num}"
                    return statement

    def read_csv_lines(self,csv_path):
        start_line = 6
        end_line = 15
        with open(csv_path, mode='r') as file:
            csv_reader = csv.reader(file)
            
            # Skip lines before the start line
            for _ in range(start_line - 1):
                next(csv_reader)
            
            # Read and store rows from start to end line
            result = []
            for i, row in enumerate(csv_reader, start=start_line):
                if i > end_line:
                    break
                result.append(row)
        
        return result
    

    def table_data(self,csv_path):
        data = self.read_csv_lines(csv_path)
        actual_data = []
        for i in range(len(data)):
            if data[i]==[]:
                break
            else:
                data1= data[i]
                temp = []
                temp.append(data1[1])
                temp.append(data1[-2])
                temp.append(data1[-1])
                actual_data.append(temp)
                
        return actual_data
    

    def extract_data(self,csv_path):
        li = self.read_csv_lines(csv_path)
        grade = []
        credits = []
        for i in range(len(li)):
            if li[i] == []:
                break
            else:
                grade.append(li[i][-2])
                credits.append(float(li[i][-1]))
        return grade,credits
    

    def change_type_of_grade(self,grade):
        try:
            final_list = []
            for i in range(len(grade)):
                if grade[i] == 'O':
                    final_list.append(int(10))
                elif grade[i] == 'A+':
                    final_list.append(int(9))
                elif grade[i] == 'A':
                    final_list.append(int(8))
                elif grade[i] == 'B+':
                    final_list.append(int(7))
                elif grade[i] == 'B':
                    final_list.append(int(6))
                elif grade[i] == 'C':
                    final_list.append(int(5))
                elif grade[i] == 'F':
                    final_list.append(int(0))
                else:
                    final_list.append(int(0))

            return final_list
        except Exception as e:
            return f"Failed to convert the grade {e}" 




    def calculate(self,csv_path):
        try:
            data = self.extract_data(csv_path)

            grade = self.change_type_of_grade(data[0])
            credits = data[1]
            sum_of_credits = sum(credits)
            temp = []
            for i in range(len(grade)):
                ans = grade[i]*credits[i]
                temp.append(ans)
            final_sum = sum(temp)
            sgpa = final_sum/sum_of_credits
            return sgpa
        except Exception as e:
            return f"Error in calculating SGPA {e} "












