# WorkDrive Admin API

## List Teams

```python
teams = await client.workdrive.admin.list_teams()
print(teams.resources)
```

## List Team Members and Team Folders

```python
members = await client.workdrive.admin.list_team_members(team_id="team_123")
folders = await client.workdrive.admin.list_team_folders(team_id="team_123")
print(members.resources, folders.resources)
```
