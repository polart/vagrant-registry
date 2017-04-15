import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual} from "lodash";
import * as actions from "../actions";
import {BOX_ORDERING, DEFAULT_BOX_ORDERING} from "../constants";
import BoxList from "./BoxList";
import {Link} from "react-router";


class UserDashPage extends Component {
  componentDidMount() {
    this.fetchBoxes();
  }

  componentDidUpdate(prevProps) {
    if (!isEqual(prevProps.location.query, this.props.location.query)) {
      // For a case, when changing page or ordering.
      this.fetchBoxes();
    }
  }

  fetchBoxes = () => {
    this.props.fetchBoxes(
        this.props.myUsername,
        this.props.location.query.page || 1,
        BOX_ORDERING[this.props.location.query.order] || DEFAULT_BOX_ORDERING,
        this.props.location.query.q
    );
  };

  render() {
    return (
        <div>
          <PageHeader>My boxes</PageHeader>
          <Link className='btn btn-success' to='/boxes/create/'>
            New box
          </Link>
          <BoxList
              router={this.props.router}
              boxes={this.props.boxes}
              boxesPages={this.props.boxesPages}
          />
        </div>
    );
  }
}

function mapStateToProps(state, props) {
  return {
    myUsername: state.myUsername,
    boxes: state.entities.boxes,
    boxesPages: state.pagination.boxes[state.myUsername],
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(UserDashPage)
