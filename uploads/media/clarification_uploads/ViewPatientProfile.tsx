import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { useRoute } from '@react-navigation/native';
import { RootStackParamList } from '../../type'; // Adjust the path to where `RootStackParamList` is defined
import { RouteProp } from '@react-navigation/native';

const ViewPatientProfile: React.FC = () => {
  // Update the route type to 'ViewPatientProfile' since no params are expected
  const route = useRoute<RouteProp<RootStackParamList, 'ViewPatientProfile'>>();

  // Directly use dummy data or fetch from storage if necessary
  const patientData = {
    patientID: '12345',
    patientName: 'John Doe',
    age: 30,
    gender: 'Male',
    education: 'Bachelor\'s Degree',
    occupation: 'Software Developer',
    maritalStatus: 'Single',
    diet: 'Vegetarian'
  };

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
          <Text style={styles.nameText}>{patientData.patientName}</Text>
        </View>
        
        {/* Patient Details */}
        <View style={styles.detailsContainer}>
          <View style={styles.row}>
            <Text style={styles.rowLabel}>Patient ID:</Text>
            <Text style={styles.rowValue}>{patientData.patientID}</Text>
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
            <Text style={styles.rowValue}>{patientData.maritalStatus}</Text>
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
