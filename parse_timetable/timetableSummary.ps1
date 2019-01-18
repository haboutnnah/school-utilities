$SubjArray =  "MATHEMATICS ADVANCED"
$FileHead = [system.String]::Join(",", $SubjArray)
$FileHead = "Last Name ,First Name ," + $FileHead
Write-Output $FileHead | Out-File -FilePath out.csv

function Get-SubjectsFromStudentID {
    param ( [int]$StudentID )
    $URI = "https://web1.normanhurb-h.schools.nsw.edu.au/timetables/timetable?student=" + $StudentID + "`&show=cyclical"
    $HTML = Invoke-WebRequest -Uri $URI -UserAgent "Script to make CSV of class names `<contact@hannahi.com`>" 
    $title = $HTML.ParsedHtml.title
    $fullname = ($title -split ' -')[0]
    $object = New-Object -TypeName PSObject
    $classObj = ($HTML.ParsedHtml.getElementsByClassName('timetable-class') | Where-Object {$_innerText -notlike '.*, .*'}).innerText
    for ($j = 0 ; $j -lt $classObj.Length; $j++){
        $subject,$classID = ((($classObj[$j] -split '\n')[0]) -split "\(") -replace "\)"
        $object | Add-Member -Name $subject -MemberType NoteProperty -Value $classID -Force -ErrorAction SilentlyContinue
    }
#    if($object."ENGLISH " -ne "None"){
    if($true){
        $toWrite = $fullname
        for ($k = 0 ; $k -le $SubjArray.Length; $k++){
            $currentSubjectIndex = $SubjArray[$k]
            $currentSubjectID = $object.$currentSubjectIndex
            $toWrite = $toWrite + "," + $currentSubjectID 
        }
        $toWrite = $toWrite -replace("`n")
        $toWrite = $toWrite -replace("`r")
        Write-Output $toWrite | Out-File -FilePath out.csv -Append
        $text = "Finished Processing " + $fullname
        Write-Host $text -ForegroundColor Green
    }
    else {
        $text = "! Failed Processing " + $fullname
        Write-Host $text -ForegroundColor Red
    }
}

for ($i = 1064; $i -lt 1187; $i++){
    # Get everyone who was in the school in the first batch
    Get-SubjectsFromStudentID($i)
}

$LaterStudents = 1191, 1335, 1339, 1334, 1361, 1363, 1364

foreach ($Student in $LaterStudents){
    Get-SubjectsFromStudentID($Student)
}



