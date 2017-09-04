<# The sample scripts are not supported under any Microsoft standard support 
 program or service. The sample scripts are provided AS IS without warranty  
 of any kind. Microsoft further disclaims all implied warranties including,  
 without limitation, any implied warranties of merchantability or of fitness for 
 a particular purpose. The entire risk arising out of the use or performance of  
 the sample scripts and documentation remains with you. In no event shall 
 Microsoft, its authors, or anyone else involved in the creation, production, or 
 delivery of the scripts be liable for any damages whatsoever (including, 
 without limitation, damages for loss of business profits, business interruption, 
 loss of business information, or other pecuniary loss) arising out of the use 
 of or inability to use the sample scripts or documentation, even if Microsoft 
 has been advised of the possibility of such damages 
#>



Param(
    [Parameter(Mandatory = $true)][String]$directory
)


$instances = (get-itemproperty 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server').InstalledInstances

#check if there is any instance installed on the computer
if($instances)
{
    #check if the directory exists or not    
    if ((Test-Path $directory) -eq $False)
    {
        Write-Host "The directory $directory doesn't exist or check the form of the directory!"
    }
    else
    {
        $smo = [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SqlServer.SMO")
        #if SQL Server version is or is higher than SQL Server 2008, load Microsoft.SqlServer.SmoExtended
        if($smo.Getname().Version.Major -ge 10)
        {
                [System.Reflection.Assembly]::LoadWithPartialName("Microsoft.SqlServer.SmoExtended") | out-null
        }

         #List all the instances in a SQL Server    
         foreach($i in $instances)
         {                                                                                                                                                                                               
            #Get the full name of the instance
            $i = $i.ToUpper()
            $computername = $env:COMPUTERNAME

            if ($i -eq "MSSQLSERVER")
            {
            $instance = $computername
            }
            else
            {
            $instance = "$($computername)\$($i)"
            }
            Write-Host "-------------------------------"
            Write-Host "This is instance: $instance"
            Write-Host "-------------------------------"

            #List all the databases in an instance
            $ins = New-Object Microsoft.SqlServer.Management.Smo.Server("$instance")
            $dbs=$ins.Databases
    
            #Back up all the databases in an instance
            foreach($db in $dbs)
            {
                $dbname = $db.Name
       
                if(($dbname.ToString()) -ne "tempdb" )
                {
                    #Get the date to name the backup 
                    $date = Get-Date -Format yyyyMMdd
        
                    $backup = New-Object Microsoft.SqlServer.Management.Smo.Backup
                    $backup.Action = [Microsoft.SqlServer.Management.Smo.BackupActionType]::Database
                    $backup.BackupSetName = $dbname + "_backup_" + $date
                    $backup.Database = $dbname
                    $backup.MediaDescription = "Disk"
                    $backup.Devices.AddDevice($directory  + "\" + $i + "_" + $dbname.ToString() + "_" + $date + ".bak", "File")
                    try
                    {Write-Progress -Activity "Please wait! Backuping SQL databases... " -Status "Processing:" -CurrentOperation "Currently processing: $db"
                    $backup.SqlBackup($ins)
                    Write-Host "$dbname backed up!"}
                    catch
                    {$dbname + " backup failed."
                    $_.Exception.Message}   
                }
            }  
         }
    } 
}  
else
{ 
    Write-Host "There is no SQL Server installed on this computer!"
}
