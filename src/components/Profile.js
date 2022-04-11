import React from "react";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  mainNav: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: '2%',
    marginBottom: '2%',
  },
  usuario: {
    marginRight: '2%',
  }
}));

const Profile = () => {

  const classes = useStyles();


  return (
    <div>
      <div className={classes.mainNav}>
        <h4 className={classes.usuario}>Administrador:</h4>
        <p></p>
      </div>
      <h4>Concursos:</h4>
    </div>
  );
};

export default Profile;
