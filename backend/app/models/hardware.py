from piccolo.columns import Date, Integer, Text, Varchar
from piccolo.table import Table


class HardwareAsset(Table):
    id = Integer(primary_key=True)
    name = Varchar(length=255)
    brand = Varchar(length=100)
    purchase_date = Date(null=True, required=False)
    status = Varchar(length=50)
    assigned_to = Varchar(length=255, null=True, required=False)
    notes = Text(null=True, required=False)
