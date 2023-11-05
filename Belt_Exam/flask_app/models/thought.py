from flask_app.config.mysqlconnection import connectToMySQL

from flask import flash
import re


from flask_app.models.user import User



class Thought:
    db = "users_thoughts"
    def __init__(self, data):
        self.id = data['id']
        self.post = data['post']
        self.user_id = data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        # new from alaa
        self.user = None
        self.users_who_favorited =[]
        self.user_ids_who_favorited = []




    @staticmethod
    def validate_thought(thought):
        is_valid = True
        if len(thought['post']) < 5:
            is_valid = False
            flash("Thought is required","thought")
            flash("Thought must be at least 5 characters","thought")

        return is_valid
    
    
    @classmethod
    def save(cls,data):
        query = "INSERT INTO thoughts (post,user_id) VALUES (%(post)s,%(user_id)s);"
        return connectToMySQL(cls.db).query_db(query, data)
    

    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM thoughts WHERE id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        return cls( results[0] ) 


    


#  for one to many :
    # @classmethod
    # def get_all(cls):
    #     query = "SELECT * FROM thoughts JOIN users ON thoughts.user_id = users.id;"

    #     results = connectToMySQL(cls.db).query_db(query)
        
    #     thoughts = []
    #     for row in results:
    #         # Creating an instance of the review
    #         thought = cls(row)

    #         # Dictionary to create the User instance
    #         user_dict = {
    #             'id': row['users.id'],
    #             'first_name': row['first_name'],
    #             'last_name': row['last_name'],
    #             'email': row['email'],
    #             'password': row['password'],
    #             'created_at': row['users.created_at'],
    #             'updated_at': row['users.updated_at'],
    #         }

    #         thought.user = User(user_dict)
    #         thoughts.append(thought)

    #     return thoughts



# Using Many to many
    @classmethod
    def get_all(cls):
        #query = "SELECT * FROM thoughts JOIN users ON thoughts.user_id = users.id ;"
        
        query = """
            select * from thoughts join users AS creators on thoughts.user_id = creators.id
            left join users_has_favorited on thoughts.id = users_has_favorited.thought_id 
            left join users as users_who_favorited on users_has_favorited.user_id = users_who_favorited.id
            ORDER BY thoughts.id;

        """
        results = connectToMySQL(cls.db).query_db(query)

        thoughts = []
        for row in results:

            new_thought = True
            users_who_favorited_data = {
                'id':row['users_who_favorited.id'],
                'first_name':row.get('users_who_favorited.first_name'),
                'last_name':row.get('users_who_favorited.last_name'),
                'email':row.get('users_who_favorited.email'),
                'password':row.get('password'),
                'created_at':row.get('users_who_favorited.created_at'),
                'updated_at':row.get('users_who_favorited.updated_at')
            }

            number_of_thoughts = len(thoughts)
            if number_of_thoughts > 0 :
                last_thought = thoughts[number_of_thoughts - 1]
                if  last_thought.id == row['id']:
                    last_thought.users_who_favorited.append(User(users_who_favorited_data))
                    last_thought.user_ids_who_favorited.append(users_who_favorited_data['id'])
                    new_thought = False

            if new_thought:
                thought = cls(row)
                user_dict = {
                    'id':row['creators.id'],
                    'first_name':row['first_name'],
                    'last_name':row['last_name'],
                    'email':row['email'],
                    'password':row['password'],
                    'created_at':row['creators.created_at'],
                    'updated_at':row['creators.updated_at']
                }
                thought.user =   User(user_dict)
                if row['users_has_favorited.id']:
                    thought.users_who_favorited.append(User(users_who_favorited_data))
                    thought.user_ids_who_favorited.append(users_who_favorited_data['id'])
                    
                thoughts.append(thought)

        return thoughts
    
        
    @classmethod 
    def delete(cls, data):
        thought_id = data ['id']
        delete_favorites_query = "DELETE FROM users_has_favorited WHERE thought_id = %(thought_id)s;"
        connectToMySQL(cls.db).query_db(delete_favorites_query, {'thought_id' : thought_id})

        
        
        delete_thought_query = "DELETE FROM thoughts WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(delete_thought_query, data)
    

    @classmethod 
    def get_by_id(cls, data): # data = {'id' : 12}
        query = "SELECT * FROM thoughts JOIN users ON users.id = thoughts.user_id WHERE thoughts.id = %(id)s;"
        
        results = connectToMySQL(cls.db).query_db(query, data)

        if len(results) < 1:
            return False
        
        row = results[0]

        thought = cls(row)
        
        user_dict = {
            'id': row['users.id'],
            'first_name': row['first_name'],
            'last_name': row['last_name'],
            'email': row['email'],
            'password': row['password'],
            'created_at': row['users.created_at'],
            'updated_at': row['users.updated_at'],
        }

        thought.user = User(user_dict)
        return thought
    

    @classmethod   
    def get_user_posts(cls,data):
        query = "SELECT * FROM thoughts WHERE user_id = %(user_id)s;"
        
        results = connectToMySQL(cls.db).query_db(query, data)

        thoughts = []
        for row in results:
            thought = cls(row)
            thoughts.append(thought)
        return thoughts


    

    @classmethod
    def favorite(cls, data):
        query = "INSERT INTO users_has_favorited (user_id, thought_id) VALUES(%(user_id)s , %(thought_id)s);"
        result = connectToMySQL(cls.db).query_db(query, data)
        return result
    
    @classmethod
    def unfavorite(cls, data):
        query = "DELETE FROM users_has_favorited WHERE review_id = %(review_id)s AND user_id = %(user_id)s;"
        result = connectToMySQL(cls.db).query_db(query , data)
        return result    




