import os
import datetime
import pymysql
import paramiko


class backup:
    def __init__(self,remote_file_path,hostname,username,password):
        self.remote_file_path=remote_file_path
        self.hostname=hostname
        self.password=password
        self.username=username
        self.backup_directory='C:/file_backup'

#____________creating backup of databases

    def create_backup(self): 
        source_conn=pymysql.connect(host="localhost", user="root")
        backup_directory='C:/file_backup'
        
        with source_conn.cursor() as cur:
            sql = "show databases"
            cur.execute(sql)
            data = cur.fetchall()
            
            for row in data:
                print(row[0])
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                backup_filename = f'{row[0]}-{timestamp}.sql'
                backup_path=os.path.join(backup_directory,backup_filename)
                
                
                command = f'mysqldump -u root --skip-column-statistics --databases {row[0]} > "{backup_path}"'
                os.system(command)
                print("Backup created successfully.====={}".format(row[0]))
                
    
#____________________uploading backup on server______________________

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname, username=username, password=password)
                
    
                sftp = ssh.open_sftp()
                sftp.put(backup_path,remote_file_path+backup_filename)
                print("backup uploaded successfully.{}".format(row[0]))
                
#_____________________deleting backup from local_________________________
                os.unlink(backup_path)
                print("Backup delete from local====>>> {}".format(row[0]))
                ssh.close()
                sftp.close()
    
    def restore_backup(self):
        ssh=paramiko.SSHClient()
        
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        
        ssh.connect(hostname=hostname,username=username,password=password)
        
        sftp=ssh.open_sftp()
        
        backup_files=sftp.listdir(self.remote_file_path)
        for file_name in backup_files:
            if file_name.endswith('.sql'):
                restore_backup_path = os.path.join(self.remote_file_path,file_name)
                print("===================================",restore_backup_path)
                restore_comand = f'mysql -u root -p < "{restore_backup_path}"'
                stdin, stdout, stderr=ssh.exec_command(restore_comand)
                print(f'Database restored from {restore_backup_path}')
                

                output = stdout.read().decode("utf-8")     
                print(output)
            sftp.close()
            
 
                

remote_file_path = '/var/www/html'
hostname = 'localhost'
username = 'ranjana'
password = 'ranjana'
backup_uploader=backup(remote_file_path,username,password,hostname)       
backup_uploader.create_backup()
backup_uploader.restore_backup()
      