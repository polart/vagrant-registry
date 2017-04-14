import React, {Component} from "react";
import {connect} from "react-redux";
import {PageHeader} from "react-bootstrap";
import {isEqual} from "lodash";
import * as actions from "../actions";
import {BOX_ORDERING, DEFAULT_BOX_ORDERING} from "../constants";
import BoxList from "./BoxList";


class BoxSearchPage extends Component {
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
        null,
        this.props.location.query.page || 1,
        BOX_ORDERING[this.props.location.query.order] || DEFAULT_BOX_ORDERING,
        this.props.location.query.q
    );
  };

  render() {
    return (
        <div>
          <PageHeader>Search results</PageHeader>
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
    boxes: state.entities.boxes,
    boxesPages: state.pagination.boxes['__search__'],
  }
}

export default connect(mapStateToProps, {
  fetchBoxes: actions.loadBoxes,
})(BoxSearchPage)
