# People Employees API

## List Employees

```python
employees = await client.people.employees.list(limit=200)
print(employees.result_rows)
```

## Get Employee

```python
employee = await client.people.employees.get(employee_id="759415000000123001")
print(employee.result_rows)
```

## Create/Update Employee

```python
await client.people.employees.create(data={"First_Name": "Taylor"})
await client.people.employees.update(
    employee_id="759415000000123001",
    data={"First_Name": "Taylor A."},
)
```
