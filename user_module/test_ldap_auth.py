from ldap3 import Server, Connection, SIMPLE, ALL

def test_ldap_connection(email, password):
    # LDAP Server configuration
    server_url = "ldaps://TCLBLRCORPDC04.titan.com:636"
    
    try:
        # Create LDAP Server object
        server = Server(server_url, get_info=ALL)
        
        # Attempt to bind (connect) to the server
        print(f"Attempting to connect to: {server_url}")
        print(f"Trying to authenticate user: {email}")
        
        # Create a connection
        connection = Connection(
            server, 
            user=email, 
            password=password, 
            authentication=SIMPLE, 
            auto_bind=True
        )
        
        # If we reach here, connection was successful
        print("✅ Connection successful!")
        print("Server Information:")
        
        # Print available attributes of the server.info object
        if server.info:
            print(f"Available attributes: {dir(server.info)}")
            print(f"Vendor: {server.info.vendor_name}")
        else:
            print("Server info is not available.")
        
        # Close the connection
        connection.unbind()
        return True
    
    except Exception as e:
        print("❌ Connection Failed!")
        print(f"Error Details: {str(e)}")
        return False

# Test the connection
email = "Nandhini.V@titan.co.in"
password = input("Enter password: ")  # Securely input password

test_ldap_connection(email, password)
