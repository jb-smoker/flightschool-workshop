<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <script src="/static/sorttable.js"></script>
    <style>
        #t01 {
          font-family: Arial, Helvetica, sans-serif;
          border-collapse: collapse;
          width: 100%;
        }
        
        #t01 td, #t01 th {
          border: 1px solid #ddd;
          padding: 8px;
        }
        
        #t01 tr:nth-child(even){background-color: #f2f2f2;}
        
        #t01 tr:hover {background-color: #ddd;}
        
        #t01 th {
          padding-top: 12px;
          padding-bottom: 12px;
          text-align: left;
          background-color: #FF4500;
          color: white;
        }
        </style>
    <title>List</title>
</head>
<body>
    <center><h3>Build Wall of Fame</h3></center>
    <table class="sortable" id="t01">
        <thead>
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Company</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Comments</th>
        </tr>
        </thead>
        % for user in users:
        <%  
        try:
            user_id = user['user_id']
        except:
            user_id = ""
        end
        try:
            email = user['email']
        except:
            email = ""
        end
        try:
            full_name = user['full_name']
        except:
            full_name = ""
        end
        try:
            company = user['company']
        except:
            company = ""
        end
        try:
            start_time = user['start_time']
        except:
            start_time = ""
        end
        try:
            completed = user['completed']
        except:
            completed = ""
        end
        try:
            comment = user['comment']
        except:
            comment = ""
        end        
        %>
        <tr>
            <td>{{user_id}}</td>
            <td>{{full_name}}</td>
            <td>{{email}}</td>
            <td>{{company}}</td>
            <td>{{start_time}}</td>
            <td>{{completed}}</td>
            <td>{{comment}}</td>
        </tr>

        % end
        
    </table>

</body>
</html>