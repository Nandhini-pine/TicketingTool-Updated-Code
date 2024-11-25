import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Image, ActivityIndicator } from 'react-native';
import { useRoute } from '@react-navigation/native';
import axios from 'axios';

const ViewPatientProfile: React.FC = () => {
  const route = useRoute();
  const { patientID } = route.params as { patientID: string };
  
  const [patientData, setPatientData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('Patient ID:', patientID); // Add this line to check the value
    const fetchPatientData = async () => {
      try {
        const response = await axios.get(`http://192.168.0.104:8000/api/api/patients/${patientID}/`);
        setPatientData(response.data);
      } catch (error) {
        setError("Failed to load patient data");
      } finally {
        setLoading(false);
      }
    };
    if (patientID) {
      fetchPatientData();
    } else {
      setError("Patient ID is undefined");
    }
  }, [patientID]);
  

  if (loading) {
    return <ActivityIndicator size="large" color="#0000ff" />;
  }

  if (error) {
    return <Text>{error}</Text>;
  }

  if (!patientData) {
    return <Text>No data available</Text>;
  }

  return (
    <View style={styles.container}>
      {/* Cover Container */}
      <View style={styles.coverContainer}>
        <Image
          source={require('../../assets/images/cover.jpg')} // Local cover image
          style={styles.vectorImage}
        />
      </View>

      {/* Profile Container */}
      <View style={styles.profileContainer}>
        {/* Profile Picture and Name */}
        <View style={styles.profileRow}>
          {/* Profile Picture Circle */}
          <View style={styles.profilePicContainer}>
            <Image
              source={require('../../assets/images/profile.jpg')} // Local profile picture
              style={styles.profilePic}
            />
          </View>
          
          {/* Name Text */}
          <Text style={styles.nameText}>{patientData.name}</Text>
        </View>
        
        {/* Patient Details */}
        <View style={styles.detailsContainer}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Patient ID:</Text>
            <Text style={styles.rowValue}>{patientData.patient_id}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Age:</Text>
            <Text style={styles.rowValue}>{patientData.age}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Gender:</Text>
            <Text style={styles.rowValue}>{patientData.gender}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Education:</Text>
            <Text style={styles.rowValue}>{patientData.education}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Occupation:</Text>
            <Text style={styles.rowValue}>{patientData.occupation}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Marital Status:</Text>
            <Text style={styles.rowValue}>{patientData.marital_status}</Text>
          </View>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Diet:</Text>
            <Text style={styles.rowValue}>{patientData.diet}</Text>
          </View>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  coverContainer: {
    position: 'relative',
    width: '75%',
    height: 270,
    justifyContent: 'center',
    alignItems: 'center',
    top: 35,
    right: -40,
  },
  vectorImage: {
    width: '90%',
    height: '90%',
    position: 'absolute',
    resizeMode: 'cover',
  },
  profileContainer: {
    width: '90%',
    maxWidth: 400,
    backgroundColor: '#f0f0f0',
    borderRadius: 35,
    padding: 20,
    alignSelf: 'center',
    position: 'absolute',
    bottom: 20,
    alignItems: 'center',
    top: 285,
  },
  profileRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    width: '100%',
  },
  profilePicContainer: {
    width: 100,
    height: 100,
    borderRadius: 50,
    borderWidth: 4,
    borderColor: '#fff',
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15, // Space between profile picture and text field
  },
  profilePic: {
    width: '100%',
    height: '100%',
    borderRadius: 50,
  },
  nameText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  detailsContainer: {
    width: '100%',
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    height: 40,
    borderBottomWidth: 1,
    borderBottomColor: '#ddd',
    alignItems: 'center',
    paddingHorizontal: 10,
  },
  rowLabel: {
    fontSize: 16,
    color: '#333',
  },
  rowValue: {
    fontSize: 16,
    color: '#666',
  },
});

export default ViewPatientProfile;
