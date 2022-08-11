from concurrent.futures.process import _python_exit
from flask import Flask, jsonify, request, Response
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/akashk/desktop/temple_database.db'
db = SQLAlchemy(app)

@app.route('/')
def index():
    return 'Temple App By Akash'

def validPostRequestData(visitorObject):
    if ("id" in visitorObject and "Name" in visitorObject and "phone" in visitorObject and "Mobile" in visitorObject and "Address" in visitorObject and "Year" in visitorObject and "Amount" in visitorObject and "thalakattu" in visitorObject and "receiptNo" in visitorObject):
        return True
    else:
        return False   


@app.route('/addvisitor', methods=['POST'])
def add_visitordata():
    print("Add Visitor Call")
    request_data = request.get_json()
    print(request_data)
    if(validPostRequestData(request_data)):
        print("Valide Post ")
        Visit.add_visitor(request_data['id'], request_data['Name'], request_data['phone'],request_data['Mobile'], request_data['Address'], request_data['Year'],request_data['Amount'], request_data['thalakattu'], request_data['receiptNo'])
        response = Response("", status = 201, mimetype='application/json')
        response.headers['Location'] = "/visitor/" + str(request_data['id'])
        return response
    else:
        invalidPostRequestDataErrorMsg = {
            "error": "Invalid visitor object passed in request",
            "helpString": "Data passed in similar to this {'Name': 'VisitorName', 'Amount': 900}"
        }
        response = Response(json.dumps(invalidPostRequestDataErrorMsg), status=400, mimetype='application/json')
        return response 

@app.route('/visitors', methods=['GET'])
def getAllVisitors():   
    return jsonify({'visitors': Visit.getAllVisitors()})

@app.route('/visitors/<int:_id>')
def getVisitorById(_id):
    print(_id)
    print(Visit.getVisitorById(_id))
    return jsonify({'visitors': Visit.getVisitorById(_id)})

@app.route('/visitors/<int:phone>')
def getVisitorByPhone(phone):
    print(phone)
    print(Visit.getVisitorByPhone(phone))
    return jsonify({'visitors': Visit.getVisitorByPhone(phone)})

@app.route('/deletvisitor/<int:_id>', methods=['DELETE'])
def delete_visitor(_id):
    if(Visit.delete_visitor(_id)):
        response = Response("", status=204)
        return response
    invalidIdErrorMsg = {
        "error": "Invalid visitor _id passed in request"
    }
    response = Response(json.dumps(invalidIdErrorMsg), status = 404, mimetype = 'application/json')
    return response;


@app.route('/updatevisitor/<int:_id>', methods=['PATCH'])
def update_visitor(_id):
    request_data = request.get_json()
    print(request_data)
    print(request_data['phone'])
    if("phone" in request_data):
        Visit.update_visitor_phone(_id, request_data['phone'])
    if("Address" in request_data):
        Visit.update_visitor_Address(_id, request_data['Address'])
    response = Response("", status=204)
    response.headers['Location'] = "/visitors/" + str(_id)
    return response  

def validPutRequestData(visitorObject):
    if ("id" in visitorObject and "Name" in visitorObject and "phone" in visitorObject and "Mobile" in visitorObject and "Address" in visitorObject and "Year" in visitorObject and "Amount" in visitorObject and "thalakattu" in visitorObject and "receiptNo" in visitorObject):
        return True
    else:
        return False  

@app.route('/replacevisitor/<int:phone>', methods=['PUT'])
def replacevisitor(phone):
    request_data = request.get_json()
    if(validPutRequestData(request_data)):
        Visit.add_visitor(request_data['id'], request_data['Name'], request_data['phone'],request_data['Mobile'], request_data['Address'], request_data['Year'],request_data['Amount'], request_data['thalakattu'], request_data['receiptNo'])
        response = Response("", status = 201, mimetype='application/json')
        response.headers['Location'] = "/visitor/" + str(request_data['id'])
        return response
    else:
        invalidPutRequestDataErrorMsg = {
            "error": "Invalid visitor object passed in request",
            "helpString": "Data passed in similar to this {'Name': 'VisitorName', 'Amount': 900}"
        }
        response = Response(json.dumps(invalidPutRequestDataErrorMsg), status=400, mimetype='application/json')
        return response

class Visit(db.Model):
    __tablename__ = 'visitor'
    _id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(80), nullable=True)
    Mobile = db.Column(db.String(80), nullable=True)
    Address = db.Column(db.String(80), nullable=True)
    Year = db.Column(db.String(80), nullable=True)
    Amount = db.Column(db.String(80), nullable=True)
    thalakattu = db.Column(db.String(80), nullable=True)
    receiptNo = db.Column(db.Integer, nullable=True)

    def json(self):
        return {'_id': self._id, 'Name': self.Name, 'phone': self.phone,'Mobile': self.Mobile, 'Address': self.Address, 'Year': self.Year,'Amount': self.Amount, 'thalakattu': self.thalakattu, 'receiptNo': self.receiptNo}
    
    def getAllVisitors():
        return [Visit.json(visit) for visit in Visit.query.all()]

    def getVisitorById(id):
        return Visit.query.filter_by(_id=id)

    def getVisitorByPhone(phone):
        return Visit.query.filter_by(phone=phone).first()    
  
    @property
    def serialize(self):
       return {
           'id'         : self.id,
           'many2many'  : self.serialize_many2many
       }    

    def add_visitor(_id,_Name,_phone,_Mobile,_Address,_Year,_Amount,_thalakattu,_receiptNo):
        print("Name :",_Name)
        new_visitor = Visit(_id = _id, Name = _Name, phone = _phone, Mobile=_Mobile, Address=_Address, Year=_Year, Amount=_Amount, thalakattu=_thalakattu, receiptNo=_receiptNo)
        db.session.add(new_visitor)
        db.session.commit()

    def delete_visitor(_id):
        is_successful = Visit.query.filter_by(_id=_id).delete()
        db.session.commit()
        return bool(is_successful)    
    
    def update_visitor_phone(_id,_phone):
        visitor_to_update = Visit.query.filter_by(_id=_id).first()
        visitor_to_update.phone = _phone
        db.session.commit()
    
    def update_visitor_Address(_id,_Address):
        address_to_update = Visit.query.filter_by(_id=_id).first()
        address_to_update.address = _Address
        db.session.commit()

    def replacevisitor(_id, _Name, _phone,_Mobile,_Address,_Year,_Amount,_thalakattu,_receiptNo):
        visitor_to_replace = Visit.query.filter_by(_phone=_phone).first()
        visitor_to_replace.Name = _Name
        visitor_to_replace.phone = _phone
        visitor_to_replace.Mobile = _Mobile
        visitor_to_replace.Address = _Address
        visitor_to_replace.Year = _Year
        visitor_to_replace.Amount = _Amount
        visitor_to_replace.thalakattu = _thalakattu
        visitor_to_replace.receiptNo = _receiptNo
        db.session.commit()


if __name__ == '__main__':
    app.run(debug=True)        

