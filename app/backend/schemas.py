from pydantic import BaseModel

class Document(BaseModel):
    กลุ่ม: str
    ลำดับ: float
    ชื่อ:str
    รายละเอียด:str
    หน่วย:str
    ค่าแฟคเตอร์:float
    ข้อมูลอ่างอิง:str
    วันที่อัพเดท:str