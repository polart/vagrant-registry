import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import * as actions from "../actions";
import BoxForm from "./BoxForm";


class BoxCreatePage extends Component {
  componentDidMount() {
    if (!this.props.myUsername) {
      this.props.router.push(`/login/?next=${location.pathname}`);
    }
  }

  onSubmit = (e) => {
    e.preventDefault();
    this.props.createBox(this.props.myUsername, this.props.form.data);
  };

  onCancel = () => {
      this.props.router.push('/');
  };

  render() {
    return (
        <div>
          <PageHeader>Create new box</PageHeader>
          <BoxForm
              pending={this.props.form.pending}
              submitTitle='Create'
              submitPendingTitle="Creating..."
              onSubmit={this.onSubmit}
              onCancel={this.onCancel}
          />
        </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    myUsername: state.myUsername,
    form: state.forms.box,
  }
}

export default connect(mapStateToProps, {
  createBox: actions.createBox,
})(BoxCreatePage)
